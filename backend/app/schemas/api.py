"""
API Request and Response DTO Schemas.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from backend.app.models.video import PlatformType, VideoStatus
from backend.app.models.job import JobStatus


class VideoSubmitRequest(BaseModel):
    """Request payload for submitting a public video URL."""
    url: str = Field(..., description="Public video URL (e.g. YouTube, Vimeo)")


class JobResponse(BaseModel):
    """Response payload representing background job status."""
    job_id: str
    status: JobStatus
    progress: int = Field(..., ge=0, le=100)
    error_message: Optional[str] = None
    video_id: str
    transcript_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TranscriptSegmentResponse(BaseModel):
    """Individual segment in transcript timestamp mode."""
    id: str
    start_time: float
    end_time: float
    duration: float
    timestamp_label: str
    text: str
    speaker: Optional[str] = None


class TranscriptResponse(BaseModel):
    """Complete transcript output with metadata and dual-mode content."""
    id: str
    video_id: str
    title: str
    source_url: Optional[str] = None
    platform: PlatformType
    duration: int
    duration_formatted: str
    language: str
    raw_text: str
    clean_text: str
    paragraphs: List[str]
    segments: List[TranscriptSegmentResponse]
    created_at: datetime


class UploadResponse(BaseModel):
    """Response payload for uploaded video processing initiation."""
    job_id: str
    status: JobStatus
    filename: str


class HealthResponse(BaseModel):
    """Service health status check response."""
    status: str
    version: str
    database: str
    redis: str
