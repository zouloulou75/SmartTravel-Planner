from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class EvaluationRequest(BaseModel):
    sample_size: int = Field(default=5, ge=1, le=20)


class EvaluationResponse(BaseModel):
    run_id: str
    sample_size: int
    metrics: dict
    results: list[dict]
    provider: str
    model: str
    created_at: datetime
