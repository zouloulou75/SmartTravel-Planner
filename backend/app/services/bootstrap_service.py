from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import init_db
from app.ml.artifact import model_artifact_exists
from app.ml.training import train_recommender
from app.repositories.examples import count_trip_examples_by_split, replace_trip_examples
from app.repositories.runs import fetch_latest_evaluation_run
from app.repositories.stats import replace_poi_stats, replace_region_stats, fetch_stats_summary
from app.schemas.metrics import MetricsSummaryResponse


class BootstrapService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    def run(self) -> dict[str, Any]:
        init_db()
        imported = self.import_trip_examples()
        trained = self.train_if_needed(force=self.settings.bootstrap_force)
        return {"imported": imported, "trained": trained}

    def import_trip_examples(self) -> dict[str, int]:
        imported_counts: dict[str, int] = {}
        for split_name in ("train", "validation", "test"):
            path = self._trip_file_path(split_name)
            frame = pd.read_csv(path)
            rows = []
            for index, row in frame.iterrows():
                rows.append(
                    {
                        "split": split_name,
                        "source_index": int(index),
                        "org": str(row.get("org", "")),
                        "dest": str(row.get("dest", "")),
                        "days": int(row.get("days", 1)),
                        "visiting_city_number": self._optional_int(row.get("visiting_city_number")),
                        "dates_json": self._ensure_jsonable(self._parse_literal(row.get("date"))),
                        "people_number": self._optional_int(row.get("people_number")),
                        "local_constraint_json": self._ensure_jsonable(
                            self._parse_literal(row.get("local_constraint"))
                        ),
                        "budget": self._optional_float(row.get("budget")),
                        "query": str(row.get("query", "")),
                        "level": self._optional_str(row.get("level")),
                        "reference_information_json": self._ensure_jsonable(
                            self._parse_literal(row.get("reference_information"))
                        ),
                        "annotated_plan_json": self._ensure_jsonable(
                            self._parse_literal(row.get("annotated_plan"))
                        ),
                    }
                )
            imported_counts[split_name] = replace_trip_examples(self.db, split_name, rows)
        return imported_counts

    def train_if_needed(self, *, force: bool = False) -> dict[str, Any]:
        stats_summary = fetch_stats_summary(self.db)
        if (
            not force
            and model_artifact_exists(self.settings.model_artifact_path)
            and stats_summary["poi_stats_count"] > 0
            and stats_summary["poi_stats_with_region_count"] > 0
            and stats_summary["region_stats_count"] > 0
        ):
            return {"skipped": True}

        output = train_recommender(
            interaction_data_path=self.settings.interaction_data_path,
            model_artifact_path=self.settings.model_artifact_path,
            sample_rows=self.settings.interaction_sample_rows,
            top_n=self.settings.training_top_n,
            candidate_pool_size=self.settings.candidate_pool_size,
        )
        replace_poi_stats(self.db, output["poi_stats_rows"])
        replace_region_stats(self.db, output["region_stats_rows"])
        return output["training_summary"]

    def metrics_summary(self) -> MetricsSummaryResponse:
        counts = count_trip_examples_by_split(self.db)
        stats_summary = fetch_stats_summary(self.db)
        latest_evaluation = fetch_latest_evaluation_run(self.db)
        latest_evaluation_payload = None
        if latest_evaluation is not None:
            latest_evaluation_payload = {
                "run_id": latest_evaluation.id,
                "sample_size": latest_evaluation.sample_size,
                "metrics": latest_evaluation.metrics_json,
                "created_at": latest_evaluation.created_at.isoformat(),
            }
        return MetricsSummaryResponse(
            provider="groq",
            model=self.settings.groq_model,
            trip_examples=counts,
            poi_stats_count=stats_summary["poi_stats_count"],
            region_stats_count=stats_summary["region_stats_count"],
            latest_evaluation=latest_evaluation_payload,
        )

    def _trip_file_path(self, split_name: str) -> Path:
        filename = f"{split_name}.xls"
        path = self.settings.trip_data_dir / filename
        if not path.exists():
            raise FileNotFoundError(
                f"Trip dataset file not found: {path}. Set TRIP_DATA_DIR correctly."
            )
        return path

    @staticmethod
    def _parse_literal(value: Any) -> Any:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return None
        text = str(value).strip()
        if not text:
            return None
        try:
            return ast.literal_eval(text)
        except (ValueError, SyntaxError):
            return text

    @staticmethod
    def _ensure_jsonable(value: Any) -> Any:
        if value is None:
            return None
        return json.loads(json.dumps(value, default=str))

    @staticmethod
    def _optional_int(value: Any) -> int | None:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return None
        return int(value)

    @staticmethod
    def _optional_float(value: Any) -> float | None:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return None
        return float(value)

    @staticmethod
    def _optional_str(value: Any) -> str | None:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return None
        text = str(value).strip()
        return text or None
