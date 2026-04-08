from sqlalchemy import text
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends

from app.core.config import get_settings
from app.db.session import get_db
from app.ml.artifact import model_artifact_exists
from app.ml.tracking import mlflow_server_reachable, mlflow_tracking_enabled
from app.schemas.health import HealthResponse


router = APIRouter()
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    db_connected = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_connected = False

    model_ready = model_artifact_exists(settings.model_artifact_path)
    llm_configured = bool(settings.groq_api_key)
    mlflow_enabled = mlflow_tracking_enabled()
    mlflow_connected = mlflow_server_reachable()
    status = "ok" if db_connected and model_ready else "degraded"
    return HealthResponse(
        status=status,
        db_connected=db_connected,
        model_ready=model_ready,
        llm_configured=llm_configured,
        mlflow_enabled=mlflow_enabled,
        mlflow_connected=mlflow_connected,
        mlflow_tracking_uri=settings.mlflow_tracking_uri if mlflow_enabled else None,
        mlflow_ui_url=settings.mlflow_ui_url if mlflow_enabled else None,
        mlflow_experiment_name=settings.mlflow_experiment_name if mlflow_enabled else None,
        mlflow_registered_model_name=(
            settings.mlflow_registered_model_name
            if mlflow_enabled and settings.mlflow_register_model
            else None
        ),
        mlflow_register_model=settings.mlflow_register_model if mlflow_enabled else False,
        mlflow_latest_alias=settings.mlflow_latest_alias if mlflow_enabled else None,
        mlflow_champion_alias=settings.mlflow_champion_alias if mlflow_enabled else None,
        provider="groq",
        model=settings.groq_model,
    )
