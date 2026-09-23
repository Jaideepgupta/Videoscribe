"""
Speech-to-Text (STT) Data Schemas.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class STTSegment(BaseModel):
    """Timestamped segment returned by an STT engine."""
    start_time: float = Field(..., description="Segment start time in seconds")
    end_time: float = Field(..., description="Segment end time in seconds")
    duration: float = Field(..., description="Segment duration in seconds")
    text: str = Field(..., description="Spoken text in segment")
    confidence: Optional[float] = Field(None, description="Confidence score 0.0 to 1.0")
    speaker: Optional[str] = Field(None, description="Speaker identification label")


class STTResult(BaseModel):
    """Full transcription result returned by an STT provider."""
    full_text: str = Field(..., description="Complete combined transcript text")
    language: str = Field("en", description="Detected or requested language code")
    duration: float = Field(0.0, description="Total audio duration in seconds")
    segments: List[STTSegment] = Field(default_factory=list, description="List of timestamped segments")
    provider_name: str = Field(..., description="Name of the STT engine used")
