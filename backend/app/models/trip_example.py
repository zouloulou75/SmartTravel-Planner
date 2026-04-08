from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TripExample(Base):
    __tablename__ = "trip_examples"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    split: Mapped[str] = mapped_column(String(16), index=True)
    source_index: Mapped[int] = mapped_column(Integer)
    org: Mapped[str] = mapped_column(String(255), index=True)
    dest: Mapped[str] = mapped_column(String(255), index=True)
    days: Mapped[int] = mapped_column(Integer)
    visiting_city_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    dates_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    people_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    local_constraint_json: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    budget: Mapped[float | None] = mapped_column(Float, nullable=True)
    query: Mapped[str] = mapped_column(Text)
    level: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reference_information_json: Mapped[list | dict | None] = mapped_column(JSON, nullable=True)
    annotated_plan_json: Mapped[list | dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
