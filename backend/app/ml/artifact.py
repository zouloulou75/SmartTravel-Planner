from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib


def model_artifact_exists(path: Path) -> bool:
    return path.exists() and path.is_file()


def save_model_artifact(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(payload, path)
    clear_model_artifact_cache()


@lru_cache(maxsize=1)
def _load_artifact(path_str: str, mtime: float) -> dict[str, Any]:
    del mtime
    return joblib.load(path_str)


def load_model_artifact(path: Path) -> dict[str, Any]:
    if not model_artifact_exists(path):
        raise FileNotFoundError(f"Model artifact not found: {path}")
    return _load_artifact(str(path), path.stat().st_mtime)


def clear_model_artifact_cache() -> None:
    _load_artifact.cache_clear()
