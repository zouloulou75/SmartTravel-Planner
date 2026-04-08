from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.base import Base


settings = get_settings()

connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.database_url,
    echo=False,
    future=True,
    pool_pre_ping=True,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app.models import (  # noqa: F401
        EvaluationRun,
        PlannerRun,
        POIStat,
        RecommendationRun,
        RegionStat,
        TripExample,
    )

    Base.metadata.create_all(bind=engine)
    _ensure_poi_stat_columns()


def _ensure_poi_stat_columns() -> None:
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    if "poi_stats" not in table_names:
        return

    existing_columns = {column["name"] for column in inspector.get_columns("poi_stats")}
    required_columns = {
        "administrative_region_id": "INTEGER",
        "state_name": "VARCHAR(120)",
        "state_abbr": "VARCHAR(16)",
        "census_division": "VARCHAR(120)",
        "region_tier": "VARCHAR(64)",
    }
    missing_columns = [
        (name, ddl) for name, ddl in required_columns.items() if name not in existing_columns
    ]
    if not missing_columns:
        return

    with engine.begin() as connection:
        for column_name, ddl in missing_columns:
            connection.execute(text(f"ALTER TABLE poi_stats ADD COLUMN {column_name} {ddl}"))
