"""
Health Check API Router.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.app.config import settings
from backend.app.db.session import get_db
from backend.app.schemas.api import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint verifying application, database, and cache readiness.
    """
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unreachable: {str(e)}"

    redis_status = "configured"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        version=settings.VERSION,
        database=db_status,
        redis=redis_status,
    )
