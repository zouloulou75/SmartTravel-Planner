from fastapi import APIRouter

from app.api.v1.routes import evaluations, health, metrics, pipeline, recommendations, trips


api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(trips.router, prefix="/trips", tags=["trips"])
api_router.include_router(pipeline.router, prefix="/pipeline", tags=["pipeline"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
api_router.include_router(evaluations.router, prefix="/evaluations", tags=["evaluations"])
