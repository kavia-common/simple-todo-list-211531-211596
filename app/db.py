"""Database configuration and session management for the todo backend."""

from __future__ import annotations

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

DEFAULT_SQLITE_URL = "sqlite:///./todo.db"


def _get_database_url() -> str:
    """Return the database URL from the environment (or a safe default)."""
    return os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)


DATABASE_URL = _get_database_url()

# `check_same_thread` is required for SQLite when using a single connection across threads.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)


# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a DB session and ensures it is closed.

    Yields:
        sqlalchemy.orm.Session: SQLAlchemy session bound to the configured engine.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
