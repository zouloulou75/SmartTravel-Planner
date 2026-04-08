from __future__ import annotations

from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models import TripExample


def replace_trip_examples(db: Session, split_name: str, rows: list[dict[str, Any]]) -> int:
    db.execute(delete(TripExample).where(TripExample.split == split_name))
    db.flush()
    db.bulk_insert_mappings(TripExample, rows)
    db.commit()
    return len(rows)


def count_trip_examples_by_split(db: Session) -> dict[str, int]:
    rows = db.execute(
        select(TripExample.split, func.count(TripExample.id)).group_by(TripExample.split)
    ).all()
    return {split_name: count for split_name, count in rows}


def fetch_prompt_examples(
    db: Session,
    org: str,
    dest: str,
    days: int,
    budget: float,
    limit: int = 3,
) -> list[TripExample]:
    lowered_org = org.lower()
    lowered_dest = dest.lower()

    exact_examples = db.scalars(
        select(TripExample)
        .where(func.lower(TripExample.org) == lowered_org)
        .where(func.lower(TripExample.dest) == lowered_dest)
        .limit(limit)
    ).all()
    if exact_examples:
        return exact_examples

    destination_examples = db.scalars(
        select(TripExample)
        .where(func.lower(TripExample.dest) == lowered_dest)
        .order_by(func.abs(TripExample.days - days), func.abs(TripExample.budget - budget))
        .limit(limit)
    ).all()
    if destination_examples:
        return destination_examples

    return db.scalars(
        select(TripExample)
        .order_by(func.abs(TripExample.days - days), func.abs(TripExample.budget - budget))
        .limit(limit)
    ).all()


def fetch_reference_match(db: Session, org: str, dest: str) -> TripExample | None:
    lowered_org = org.lower()
    lowered_dest = dest.lower()
    exact = db.scalar(
        select(TripExample)
        .where(func.lower(TripExample.org) == lowered_org)
        .where(func.lower(TripExample.dest) == lowered_dest)
        .limit(1)
    )
    if exact is not None:
        return exact

    return db.scalar(
        select(TripExample)
        .where(func.lower(TripExample.dest) == lowered_dest)
        .limit(1)
    )


def fetch_validation_examples(db: Session, limit: int) -> list[TripExample]:
    return db.scalars(
        select(TripExample)
        .where(TripExample.split == "validation")
        .limit(limit)
    ).all()
