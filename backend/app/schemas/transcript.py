"""
Transcript Processing and Output Schemas.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ProcessedSegment(BaseModel):
    """Cleaned timestamped segment for Timestamp Mode viewing."""
    start_time: float = Field(..., description="Segment start time in seconds")
    end_time: float = Field(..., description="Segment end time in seconds")
    duration: float = Field(..., description="Segment duration in seconds")
    text: str = Field(..., description="Cleaned segment spoken text")
    formatted_start_time: str = Field(..., description="Formatted start timestamp string (MM:SS or HH:MM:SS)")
    formatted_end_time: str = Field(..., description="Formatted end timestamp string (MM:SS or HH:MM:SS)")
    speaker: Optional[str] = Field(None, description="Speaker name or tag if detected")


class ProcessedTranscript(BaseModel):
    """Complete cleaned transcript payload providing both Reading Mode and Timestamp Mode data."""
    raw_text: str = Field(..., description="Original uncleaned raw transcript")
    clean_text: str = Field(..., description="Clean continuous text formatted in readable prose")
    paragraphs: List[str] = Field(default_factory=list, description="Paragraph-chunked reading text")
    segments: List[ProcessedSegment] = Field(default_factory=list, description="Timestamp-aligned segment blocks")
    language: str = Field("en", description="Language code")
    duration: int = Field(0, description="Total duration in seconds")
