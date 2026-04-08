from uuid import uuid4

from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends

from app.db.session import get_db
from app.schemas.trip import PipelineRequest, PipelineResponse
from app.services.planner_service import PlannerService
from app.services.recommendation_service import RecommendationService


router = APIRouter()


@router.post("/plan", response_model=PipelineResponse)
def run_pipeline(payload: PipelineRequest, db: Session = Depends(get_db)) -> PipelineResponse:
    pipeline_run_id = str(uuid4())
    recommendation = RecommendationService(db).recommend(
        payload.recommendation,
        pipeline_run_id=pipeline_run_id,
    )
    trip_payload = payload.trip.model_copy(
        update={"poi_ids": [item.poi_id for item in recommendation.items]},
    )
    trip = PlannerService(db).plan_trip(trip_payload, pipeline_run_id=pipeline_run_id)
    return PipelineResponse(run_id=pipeline_run_id, recommendation=recommendation, trip=trip)
