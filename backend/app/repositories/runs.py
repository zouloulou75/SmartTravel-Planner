from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import EvaluationRun, PlannerRun, RecommendationRun


def save_recommendation_run(db: Session, run: RecommendationRun) -> RecommendationRun:
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def save_planner_run(db: Session, run: PlannerRun) -> PlannerRun:
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def save_evaluation_run(db: Session, run: EvaluationRun) -> EvaluationRun:
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def fetch_latest_evaluation_run(db: Session) -> EvaluationRun | None:
    return db.scalar(
        select(EvaluationRun).order_by(EvaluationRun.created_at.desc()).limit(1)
    )
