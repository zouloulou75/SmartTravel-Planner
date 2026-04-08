from __future__ import annotations

from statistics import mean

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import EvaluationRun
from app.repositories.examples import fetch_validation_examples
from app.repositories.runs import save_evaluation_run
from app.schemas.evaluation import EvaluationResponse
from app.schemas.trip import TripPlanRequest
from app.services.planner_service import PlannerService


class EvaluationService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    def evaluate(self, sample_size: int | None = None) -> EvaluationResponse:
        if not self.settings.groq_api_key:
            raise HTTPException(status_code=503, detail="GROQ_API_KEY is not configured.")

        target_sample_size = sample_size or self.settings.evaluation_default_sample_size
        examples = fetch_validation_examples(self.db, target_sample_size)
        planner = PlannerService(self.db)
        results = []

        for example in examples:
            payload = TripPlanRequest(
                org=example.org,
                dest=example.dest,
                days=example.days,
                budget=example.budget or 1000,
                people_number=example.people_number or 1,
                constraint_text="",
                query=example.query,
            )
            generated = planner.plan_trip(payload, persist=False)
            filled_attractions = sum(1 for day in generated.itinerary if day.attraction and day.attraction != "-")
            parse_success = 1 if generated.itinerary else 0
            days_match = 1 if len(generated.itinerary) == example.days else 0
            attraction_fill_ratio = filled_attractions / max(example.days, 1)
            score = mean([parse_success, days_match, attraction_fill_ratio])
            results.append(
                {
                    "org": example.org,
                    "dest": example.dest,
                    "parse_success": parse_success,
                    "days_match": days_match,
                    "attraction_fill_ratio": round(attraction_fill_ratio, 3),
                    "score": round(score, 3),
                }
            )

        if not results:
            raise HTTPException(status_code=404, detail="No validation examples available.")

        metrics = {
            "avg_parse_success": round(mean(item["parse_success"] for item in results), 3),
            "avg_days_match": round(mean(item["days_match"] for item in results), 3),
            "avg_attraction_fill_ratio": round(
                mean(item["attraction_fill_ratio"] for item in results),
                3,
            ),
            "avg_score": round(mean(item["score"] for item in results), 3),
        }
        run = EvaluationRun(
            sample_size=len(results),
            provider="groq",
            model=self.settings.groq_model,
            metrics_json=metrics,
            results_json=results,
        )
        saved = save_evaluation_run(self.db, run)
        return EvaluationResponse(
            run_id=saved.id,
            sample_size=saved.sample_size,
            metrics=metrics,
            results=results,
            provider=saved.provider,
            model=saved.model,
            created_at=saved.created_at,
        )
