from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class RecommendationRequest(BaseModel):
    weather_label: str
    travel_mode_label: str
    census_division: str
    region_tier: str
    hour: int = Field(ge=0, le=23)
    day_of_week: int = Field(ge=0, le=6)
    month: int | None = Field(default=None, ge=1, le=12)
    top_k: int = Field(default=5, ge=1, le=20)

    @field_validator("weather_label", "travel_mode_label", "census_division", "region_tier")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return value.strip()


class POIRecommendationItem(BaseModel):
    poi_id: int
    rank: int
    score: float
    administrative_region_id: int | None = None
    state_name: str | None = None
    state_abbr: str | None = None
    census_division: str | None = None
    region_tier: str | None = None
    region_label: str | None = None


class RecommendationResponse(BaseModel):
    run_id: str
    context: dict
    items: list[POIRecommendationItem]
    created_at: datetime
