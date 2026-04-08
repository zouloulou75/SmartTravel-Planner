from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends

from app.db.session import get_db
from app.schemas.evaluation import EvaluationRequest, EvaluationResponse
from app.services.evaluation_service import EvaluationService


router = APIRouter()


@router.post("/run", response_model=EvaluationResponse)
def run_evaluation(
    payload: EvaluationRequest,
    db: Session = Depends(get_db),
) -> EvaluationResponse:
    service = EvaluationService(db)
    return service.evaluate(sample_size=payload.sample_size)
