from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends

from app.db.session import get_db
from app.schemas.trip import TripPlanRequest, TripPlanResponse
from app.services.planner_service import PlannerService


router = APIRouter()


@router.post("/plan", response_model=TripPlanResponse)
def plan_trip(payload: TripPlanRequest, db: Session = Depends(get_db)) -> TripPlanResponse:
    service = PlannerService(db)
    return service.plan_trip(payload)
