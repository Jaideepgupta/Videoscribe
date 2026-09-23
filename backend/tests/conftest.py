"""
Pytest configuration and global shared fixtures.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.app.db.base import Base


@pytest.fixture
def test_db_session():
    """Create an isolated in-memory SQLite database session for unit and integration tests."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, expire_on_commit=False)

    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
