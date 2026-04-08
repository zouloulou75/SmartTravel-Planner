from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pandas as pd
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.ml.artifact import load_model_artifact
from app.models import RecommendationRun
from app.repositories.runs import save_recommendation_run
from app.repositories.stats import fetch_region_stat, fetch_top_poi_stats
from app.schemas.recommendation import (
    POIRecommendationItem,
    RecommendationRequest,
    RecommendationResponse,
)


class RecommendationService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    def recommend(
        self,
        payload: RecommendationRequest,
        *,
        pipeline_run_id: str | None = None,
    ) -> RecommendationResponse:
        try:
            artifact = load_model_artifact(self.settings.model_artifact_path)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        region_stat = fetch_region_stat(
            self.db,
            census_division=payload.census_division,
            region_tier=payload.region_tier,
        )
        region_freq = float(region_stat.region_freq_median) if region_stat is not None else 1.0

        candidate_pool = fetch_top_poi_stats(
            self.db,
            limit=artifact.get("candidate_pool_size", self.settings.candidate_pool_size),
        )
        if not candidate_pool:
            raise HTTPException(
                status_code=503,
                detail="POI statistics are not loaded. Run bootstrap first.",
            )

        month = payload.month or datetime.now(UTC).month
        context = {
            "weather_label": payload.weather_label,
            "travel_mode_label": payload.travel_mode_label,
            "census_division": payload.census_division,
            "region_tier": payload.region_tier,
            "region_freq": region_freq,
            "month": month,
            "hour": payload.hour,
            "day_of_week": payload.day_of_week,
        }

        candidate_rows: list[dict[str, Any]] = []
        for stat in candidate_pool:
            candidate_rows.append(
                {
                    **context,
                    "poi_freq": stat.poi_freq,
                    "poi_id": stat.poi_id,
                    "administrative_region_id": stat.administrative_region_id,
                    "state_name": self._clean_region_value(stat.state_name),
                    "state_abbr": stat.state_abbr,
                    "census_division": self._clean_region_value(stat.census_division)
                    or context["census_division"],
                    "region_tier": stat.region_tier or context["region_tier"],
                }
            )

        features = pd.DataFrame(candidate_rows)[artifact["all_features"]]
        proba = artifact["model"].predict_proba(features)
        class_index = {int(label): idx for idx, label in enumerate(artifact["model"].classes_)}

        scored_items = []
        for row_index, candidate in enumerate(candidate_rows):
            poi_id = int(candidate["poi_id"])
            score = float(proba[row_index][class_index.get(poi_id, 0)]) if poi_id in class_index else 0.0
            scored_items.append({**candidate, "poi_id": poi_id, "score": score})

        scored_items.sort(key=lambda item: item["score"], reverse=True)
        selected = scored_items[: payload.top_k]
        items = [
            POIRecommendationItem(
                poi_id=item["poi_id"],
                rank=index + 1,
                score=item["score"],
                administrative_region_id=item.get("administrative_region_id"),
                state_name=item.get("state_name"),
                state_abbr=item.get("state_abbr"),
                census_division=item.get("census_division"),
                region_tier=item.get("region_tier"),
                region_label=self._build_region_label(item),
            )
            for index, item in enumerate(selected)
        ]

        run = RecommendationRun(
            id=str(uuid4()),
            pipeline_run_id=pipeline_run_id,
            top_k=payload.top_k,
            request_context_json=context,
            response_items_json=[item.model_dump() for item in items],
        )
        saved = save_recommendation_run(self.db, run)
        return RecommendationResponse(
            run_id=saved.id,
            context=context,
            items=items,
            created_at=saved.created_at,
        )

    @staticmethod
    def _build_region_label(item: dict[str, Any]) -> str:
        state_name = RecommendationService._clean_region_value(item.get("state_name"))
        census_division = RecommendationService._clean_region_value(item.get("census_division"))
        region_tier = RecommendationService._clean_region_value(item.get("region_tier"))
        parts = [part for part in [state_name, census_division, region_tier] if part]
        if parts:
            return " • ".join(parts)
        return f"Region #{item['poi_id']}"

    @staticmethod
    def _clean_region_value(value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        if not text or text.lower() == "unknown":
            return None
        return text
