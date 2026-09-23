"""
Video2Content (VideoScribe) FastAPI Application Entrypoint.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.core.error_handlers import register_error_handlers
from backend.app.api.v1 import api_v1_router

# Initialize FastAPI Application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="A modern platform that extracts clean, readable text transcripts from video URLs and uploaded files.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Custom Error Handlers
register_error_handlers(app)

# Mount API Routers
app.include_router(api_v1_router)


@app.get("/", tags=["Root"])
def root():
    """Service status and quick links."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs",
        "api_v1": "/api/v1",
    }
