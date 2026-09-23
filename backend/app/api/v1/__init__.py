"""
API v1 Router Aggregator.
"""

from fastapi import APIRouter
from backend.app.api.v1.videos import router as videos_router
from backend.app.api.v1.uploads import router as uploads_router
from backend.app.api.v1.jobs import router as jobs_router
from backend.app.api.v1.transcripts import router as transcripts_router
from backend.app.api.v1.health import router as health_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(videos_router)
api_v1_router.include_router(uploads_router)
api_v1_router.include_router(jobs_router)
api_v1_router.include_router(transcripts_router)
api_v1_router.include_router(health_router)
