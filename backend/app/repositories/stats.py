from __future__ import annotations

from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models import POIStat, RegionStat


def replace_poi_stats(db: Session, rows: list[dict[str, Any]]) -> int:
    db.execute(delete(POIStat))
    db.flush()
    db.bulk_insert_mappings(POIStat, rows)
    db.commit()
    return len(rows)


def replace_region_stats(db: Session, rows: list[dict[str, Any]]) -> int:
    db.execute(delete(RegionStat))
    db.flush()
    db.bulk_insert_mappings(RegionStat, rows)
    db.commit()
    return len(rows)


def fetch_top_poi_stats(db: Session, limit: int) -> list[POIStat]:
    return db.scalars(
        select(POIStat).order_by(POIStat.popularity_rank.asc()).limit(limit)
    ).all()


def fetch_region_stat(db: Session, census_division: str, region_tier: str) -> RegionStat | None:
    exact = db.scalar(
        select(RegionStat)
        .where(RegionStat.census_division == census_division)
        .where(RegionStat.region_tier == region_tier)
        .limit(1)
    )
    if exact is not None:
        return exact

    return db.scalar(
        select(RegionStat)
        .where(RegionStat.region_tier == region_tier)
        .order_by(RegionStat.sample_count.desc())
        .limit(1)
    )


def fetch_stats_summary(db: Session) -> dict[str, int]:
    poi_count = db.scalar(select(func.count(POIStat.poi_id))) or 0
    poi_with_region_count = (
        db.scalar(select(func.count(POIStat.poi_id)).where(POIStat.region_tier.is_not(None))) or 0
    )
    region_count = db.scalar(select(func.count(RegionStat.id))) or 0
    return {
        "poi_stats_count": poi_count,
        "poi_stats_with_region_count": poi_with_region_count,
        "region_stats_count": region_count,
    }
