from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends

from app.db.session import get_db
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from app.services.recommendation_service import RecommendationService


router = APIRouter()


@router.post("/pois", response_model=RecommendationResponse)
def recommend_pois(
    payload: RecommendationRequest,
    db: Session = Depends(get_db),
) -> RecommendationResponse:
    service = RecommendationService(db)
    return service.recommend(payload)
