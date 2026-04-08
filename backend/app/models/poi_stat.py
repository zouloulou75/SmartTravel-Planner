from __future__ import annotations

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class POIStat(Base):
    __tablename__ = "poi_stats"

    poi_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    poi_freq: Mapped[int] = mapped_column(Integer, nullable=False)
    popularity_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    relative_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    administrative_region_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    state_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    state_abbr: Mapped[str | None] = mapped_column(String(16), nullable=True)
    census_division: Mapped[str | None] = mapped_column(String(120), nullable=True)
    region_tier: Mapped[str | None] = mapped_column(String(64), nullable=True)
