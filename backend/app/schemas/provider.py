"""
Provider and Ingestion Data Schemas.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from backend.app.models.video import PlatformType


class RawCaptionSegment(BaseModel):
    """Raw caption segment with timestamps and text."""
    start_time: float = Field(..., description="Segment start time in seconds")
    end_time: float = Field(..., description="Segment end time in seconds")
    duration: float = Field(..., description="Segment duration in seconds")
    text: str = Field(..., description="Spoken text in segment")
    speaker: Optional[str] = Field(None, description="Speaker name or label if detected")


class VideoMetadata(BaseModel):
    """Extracted video metadata."""
    title: str = Field(..., description="Video title")
    duration: int = Field(0, description="Video duration in seconds")
    platform: PlatformType = Field(PlatformType.YOUTUBE, description="Source video platform")
    canonical_url: str = Field(..., description="Canonicalized source URL")
    author: Optional[str] = Field(None, description="Channel / creator name")
    thumbnail_url: Optional[str] = Field(None, description="Video thumbnail image URL")
    description: Optional[str] = Field(None, description="Video description snippet")
    language: str = Field("en", description="Primary detected language code")
    has_captions: bool = Field(False, description="Whether captions/subtitles are natively available")


class CaptionExtractionResult(BaseModel):
    """Result of caption extraction."""
    language: str
    is_generated: bool
    segments: List[RawCaptionSegment]
    raw_full_text: str
