from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    db_connected: bool
    model_ready: bool
    llm_configured: bool
    mlflow_enabled: bool
    mlflow_connected: bool
    mlflow_tracking_uri: str | None
    mlflow_ui_url: str | None
    mlflow_experiment_name: str | None
    mlflow_registered_model_name: str | None
    mlflow_register_model: bool
    mlflow_latest_alias: str | None
    mlflow_champion_alias: str | None
    provider: str
    model: str
