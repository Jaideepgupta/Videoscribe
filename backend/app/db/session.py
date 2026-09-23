"""
Database Session Management and Connection Pool Configuration.
Supports PostgreSQL with automatic local SQLite fallback if PostgreSQL is offline.
"""

import logging
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from backend.app.config import settings
from backend.app.db.base import Base

logger = logging.getLogger(__name__)


def create_resilient_engine():
    """Creates database engine with automatic fallback to SQLite if PostgreSQL is unreachable."""
    db_url = settings.DATABASE_URL
    connect_args = {}

    if db_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        eng = create_engine(db_url, connect_args=connect_args, echo=False)
        Base.metadata.create_all(bind=eng)
        return eng

    try:
        # Try connecting to PostgreSQL
        eng = create_engine(
            db_url,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 3},
            echo=False,
        )
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(f"Connected successfully to primary database: {db_url.split('@')[-1]}")
        return eng
    except Exception as e:
        logger.warning(
            f"Could not connect to PostgreSQL ({e}). Falling back to local SQLite database: 'sqlite:///./videoscribe.db'"
        )
        sqlite_url = "sqlite:///./videoscribe.db"
        eng = create_engine(sqlite_url, connect_args={"check_same_thread": False}, echo=False)
        Base.metadata.create_all(bind=eng)
        return eng


engine = create_resilient_engine()

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a transactional database session per request.
    Automatically closes session upon completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
