from __future__ import annotations

from contextlib import contextmanager
import json
import logging
from pathlib import Path
import tempfile
import time
from typing import Any, Iterator

import httpx
import pandas as pd
from sklearn.pipeline import Pipeline

from app.core.config import get_settings


logger = logging.getLogger(__name__)


def mlflow_tracking_enabled() -> bool:
    settings = get_settings()
    return settings.mlflow_enabled and bool(settings.mlflow_tracking_uri)


def mlflow_server_reachable() -> bool:
    settings = get_settings()
    if not mlflow_tracking_enabled():
        return False

    tracking_uri = settings.mlflow_tracking_uri.strip()
    if not tracking_uri.startswith(("http://", "https://")):
        return True

    try:
        response = httpx.get(
            tracking_uri,
            timeout=3.0,
            follow_redirects=True,
        )
        return response.status_code < 500
    except httpx.HTTPError:
        return False


@contextmanager
def maybe_start_training_run(
    *,
    run_name: str,
    tags: dict[str, Any] | None = None,
) -> Iterator[bool]:
    settings = get_settings()
    if not mlflow_tracking_enabled():
        yield False
        return

    try:
        import mlflow
    except ImportError:
        logger.warning("MLflow is enabled but the package is not installed.")
        yield False
        return

    try:
        _configure_tracking(mlflow)
    except Exception as exc:  # pragma: no cover - external service availability
        logger.warning("MLflow tracking is unavailable: %s", exc)
        yield False
        return

    run_tags = {
        "project": "travel-ml-project",
        "component": "poi-recommender-training",
        "environment": settings.environment,
        **(tags or {}),
    }

    with mlflow.start_run(
        run_name=run_name,
        nested=mlflow.active_run() is not None,
        tags={key: str(value) for key, value in run_tags.items()},
    ):
        yield True


def log_training_run(
    *,
    model: Pipeline,
    training_params: dict[str, Any],
    training_summary: dict[str, float | int],
    feature_sample: pd.DataFrame,
    poi_stats_df: pd.DataFrame,
    region_stats_df: pd.DataFrame,
    model_artifact_path: Path,
) -> None:
    if not mlflow_tracking_enabled():
        return

    try:
        import mlflow
        import mlflow.sklearn
        from mlflow.models import infer_signature
    except ImportError:
        logger.warning("MLflow logging skipped because the package is not installed.")
        return

    if mlflow.active_run() is None:
        logger.warning("MLflow logging skipped because there is no active run.")
        return

    settings = get_settings()
    sanitized_params = {
        key: str(value) if isinstance(value, Path) else value
        for key, value in training_params.items()
    }
    mlflow.log_params(sanitized_params)
    mlflow.log_metrics(training_summary)

    model_log_kwargs: dict[str, Any] = {}
    if settings.mlflow_register_model and settings.mlflow_registered_model_name:
        model_log_kwargs["registered_model_name"] = settings.mlflow_registered_model_name
        model_log_kwargs["await_registration_for"] = settings.mlflow_registration_wait_seconds

    sample = feature_sample.head(5).copy()
    if not sample.empty:
        signature = infer_signature(sample, model.predict(sample))
        model_info = mlflow.sklearn.log_model(
            model,
            artifact_path=settings.mlflow_model_name,
            signature=signature,
            input_example=sample,
            **model_log_kwargs,
        )
    else:
        model_info = mlflow.sklearn.log_model(
            model,
            artifact_path=settings.mlflow_model_name,
            **model_log_kwargs,
        )

    mlflow.log_text(
        json.dumps(training_summary, indent=2),
        "reports/training_summary.json",
    )
    mlflow.log_text(
        json.dumps(sanitized_params, indent=2),
        "reports/training_params.json",
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        poi_stats_path = temp_path / "poi_stats.csv"
        region_stats_path = temp_path / "region_stats.csv"
        poi_stats_df.to_csv(poi_stats_path, index=False)
        region_stats_df.to_csv(region_stats_path, index=False)
        mlflow.log_artifact(str(poi_stats_path), artifact_path="reports")
        mlflow.log_artifact(str(region_stats_path), artifact_path="reports")

    if model_artifact_path.exists():
        mlflow.log_artifact(str(model_artifact_path), artifact_path="exports")

    if settings.mlflow_register_model and settings.mlflow_registered_model_name:
        _finalize_registered_model(
            training_summary=training_summary,
            model_info=model_info,
        )


def _configure_tracking(mlflow_module: Any) -> None:
    settings = get_settings()
    mlflow_module.set_tracking_uri(settings.mlflow_tracking_uri)
    last_error: Exception | None = None

    for attempt in range(1, settings.mlflow_connection_retries + 1):
        try:
            mlflow_module.set_experiment(settings.mlflow_experiment_name)
            return
        except Exception as exc:  # pragma: no cover - external service availability
            last_error = exc
            if attempt == settings.mlflow_connection_retries:
                break
            time.sleep(settings.mlflow_connection_retry_delay_seconds)

    if last_error is not None:
        raise last_error


def _finalize_registered_model(
    *,
    training_summary: dict[str, float | int],
    model_info: Any,
) -> None:
    settings = get_settings()
    registered_model_name = settings.mlflow_registered_model_name
    model_version = getattr(model_info, "registered_model_version", None)
    run_id = getattr(model_info, "run_id", None)

    if not registered_model_name or model_version is None:
        return

    try:
        from mlflow.tracking import MlflowClient
    except ImportError:
        logger.warning("MLflow registry update skipped because MlflowClient is unavailable.")
        return

    try:
        client = MlflowClient(tracking_uri=settings.mlflow_tracking_uri)
        _set_model_version_tags(
            client=client,
            registered_model_name=registered_model_name,
            model_version=str(model_version),
            run_id=run_id,
            training_summary=training_summary,
        )
        _update_registered_model_aliases(
            client=client,
            registered_model_name=registered_model_name,
            model_version=str(model_version),
            training_summary=training_summary,
            champion_alias=settings.mlflow_champion_alias,
            latest_alias=settings.mlflow_latest_alias,
        )
    except Exception as exc:  # pragma: no cover - external service availability
        logger.warning("MLflow registry update skipped: %s", exc)


def _set_model_version_tags(
    *,
    client: Any,
    registered_model_name: str,
    model_version: str,
    run_id: str | None,
    training_summary: dict[str, float | int],
) -> None:
    if run_id:
        client.set_model_version_tag(
            name=registered_model_name,
            version=model_version,
            key="run_id",
            value=run_id,
        )

    for key, value in training_summary.items():
        client.set_model_version_tag(
            name=registered_model_name,
            version=model_version,
            key=key,
            value=str(value),
        )


def _update_registered_model_aliases(
    *,
    client: Any,
    registered_model_name: str,
    model_version: str,
    training_summary: dict[str, float | int],
    champion_alias: str | None,
    latest_alias: str | None,
) -> None:
    latest_alias = (latest_alias or "").strip()
    champion_alias = (champion_alias or "").strip()
    current_accuracy = None
    candidate_accuracy = _coerce_metric(training_summary.get("accuracy"))

    if latest_alias:
        try:
            client.set_registered_model_alias(
                name=registered_model_name,
                alias=latest_alias,
                version=model_version,
            )
        except Exception as exc:
            logger.warning("MLflow latest alias update skipped: %s", exc)

    if not champion_alias:
        return

    try:
        champion_version = client.get_model_version_by_alias(
            name=registered_model_name,
            alias=champion_alias,
        )
        if str(champion_version.version) != str(model_version):
            champion_run = client.get_run(champion_version.run_id)
            current_accuracy = _coerce_metric(champion_run.data.metrics.get("accuracy"))
    except Exception:
        current_accuracy = None

    if current_accuracy is None or candidate_accuracy >= current_accuracy:
        try:
            client.set_registered_model_alias(
                name=registered_model_name,
                alias=champion_alias,
                version=model_version,
            )
        except Exception as exc:
            logger.warning("MLflow champion alias update skipped: %s", exc)


def _coerce_metric(value: float | int | str | None) -> float:
    if value is None:
        return float("-inf")

    try:
        return float(value)
    except (TypeError, ValueError):
        return float("-inf")
