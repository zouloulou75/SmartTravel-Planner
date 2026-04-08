from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.recommendation import RecommendationRequest, RecommendationResponse


class TripPlanRequest(BaseModel):
    org: str
    dest: str
    days: int = Field(ge=1, le=14)
    budget: float = Field(gt=0)
    people_number: int = Field(default=1, ge=1, le=20)
    constraint_text: str = ""
    query: str
    poi_ids: list[int] | None = None


class DayPlan(BaseModel):
    day: int
    city: str
    transport: str
    breakfast: str
    lunch: str
    dinner: str
    attraction: str
    accommodation: str


class TripPlanResponse(BaseModel):
    run_id: str
    summary: dict
    itinerary: list[DayPlan]
    provider: str
    model: str
    dataset_match: bool
    created_at: datetime


class PipelineRequest(BaseModel):
    recommendation: RecommendationRequest
    trip: TripPlanRequest


class PipelineResponse(BaseModel):
    run_id: str
    recommendation: RecommendationResponse
    trip: TripPlanResponse
