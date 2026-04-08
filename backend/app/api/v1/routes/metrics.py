from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends

from app.db.session import get_db
from app.schemas.metrics import MetricsSummaryResponse
from app.services.bootstrap_service import BootstrapService


router = APIRouter()


@router.get("/summary", response_model=MetricsSummaryResponse)
def metrics_summary(db: Session = Depends(get_db)) -> MetricsSummaryResponse:
    service = BootstrapService(db)
    return service.metrics_summary()
