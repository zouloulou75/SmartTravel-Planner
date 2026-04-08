from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base


@pytest.fixture()
def db_session(tmp_path: Path) -> Session:
    db_path = tmp_path / 'test.db'
    engine = create_engine(f'sqlite:///{db_path}', future=True)
    Base.metadata.create_all(bind=engine)
    testing_session = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)
    session = testing_session()
    try:
      yield session
    finally:
      session.close()
