from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_TRIP_DATA_DIR = PROJECT_ROOT.parent / "projet ml"


class Settings(BaseSettings):
    app_name: str = "Travel ML API"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = Field(default="sqlite:///./travel_ml.db", alias="DATABASE_URL")
    cors_origins_raw: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        alias="CORS_ORIGINS",
    )

    postgres_db: str = Field(default="travel_ml", alias="POSTGRES_DB")
    postgres_user: str = Field(default="travel_ml", alias="POSTGRES_USER")
    postgres_password: str = Field(default="travel_ml", alias="POSTGRES_PASSWORD")

    pgadmin_default_email: str = Field(
        default="admin@example.com",
        alias="PGADMIN_DEFAULT_EMAIL",
    )
    pgadmin_default_password: str = Field(
        default="admin",
        alias="PGADMIN_DEFAULT_PASSWORD",
    )

    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.1-8b-instant", alias="GROQ_MODEL")
    groq_api_url: str = Field(
        default="https://api.groq.com/openai/v1/chat/completions",
        alias="GROQ_API_URL",
    )
    groq_timeout_seconds: int = Field(default=90, alias="GROQ_TIMEOUT_SECONDS")

    mlflow_enabled: bool = Field(default=True, alias="MLFLOW_ENABLED")
    mlflow_tracking_uri: str = Field(
        default="http://localhost:5001",
        alias="MLFLOW_TRACKING_URI",
    )
    mlflow_experiment_name: str = Field(
        default="travel-ml-recommender",
        alias="MLFLOW_EXPERIMENT_NAME",
    )
    mlflow_ui_url: str = Field(default="http://localhost:5001", alias="MLFLOW_UI_URL")
    mlflow_artifact_root: str = Field(
        default="file:///mlflow/artifacts",
        alias="MLFLOW_ARTIFACT_ROOT",
    )
    mlflow_model_name: str = Field(default="poi_recommender", alias="MLFLOW_MODEL_NAME")
    mlflow_register_model: bool = Field(default=True, alias="MLFLOW_REGISTER_MODEL")
    mlflow_registered_model_name: str = Field(
        default="poi_recommender",
        alias="MLFLOW_REGISTERED_MODEL_NAME",
    )
    mlflow_latest_alias: str = Field(default="candidate", alias="MLFLOW_LATEST_ALIAS")
    mlflow_champion_alias: str = Field(default="champion", alias="MLFLOW_CHAMPION_ALIAS")
    mlflow_registration_wait_seconds: int = Field(
        default=120,
        alias="MLFLOW_REGISTRATION_WAIT_SECONDS",
    )
    mlflow_connection_retries: int = Field(default=6, alias="MLFLOW_CONNECTION_RETRIES")
    mlflow_connection_retry_delay_seconds: int = Field(
        default=2,
        alias="MLFLOW_CONNECTION_RETRY_DELAY_SECONDS",
    )

    interaction_data_path: Path = Field(
        default=PROJECT_ROOT / "dataset" / "interaction_5.csv",
        alias="INTERACTION_DATA_PATH",
    )
    trip_data_dir: Path = Field(default=DEFAULT_TRIP_DATA_DIR, alias="TRIP_DATA_DIR")
    model_artifact_path: Path = Field(
        default=PROJECT_ROOT / "backend" / "artifacts" / "poi_recommender.joblib",
        alias="MODEL_ARTIFACT_PATH",
    )

    interaction_sample_rows: int = Field(default=250_000, alias="INTERACTION_SAMPLE_ROWS")
    training_top_n: int = Field(default=50, alias="TRAINING_TOP_N")
    candidate_pool_size: int = Field(default=100, alias="CANDIDATE_POOL_SIZE")
    bootstrap_force: bool = Field(default=False, alias="BOOTSTRAP_FORCE")

    evaluation_default_sample_size: int = Field(
        default=5,
        alias="EVALUATION_DEFAULT_SAMPLE_SIZE",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        protected_namespaces=(),
    )

    @property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.cors_origins_raw.split(",") if item.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
