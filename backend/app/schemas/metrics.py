from __future__ import annotations

from pydantic import BaseModel


class MetricsSummaryResponse(BaseModel):
    provider: str
    model: str
    trip_examples: dict[str, int]
    poi_stats_count: int
    region_stats_count: int
    latest_evaluation: dict | None
