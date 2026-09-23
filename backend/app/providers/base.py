"""
Base Platform Adapter Interface.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from backend.app.schemas.provider import VideoMetadata, CaptionExtractionResult, RawCaptionSegment


class BasePlatformAdapter(ABC):
    """Abstract interface for video platform ingestion adapters."""

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """Check if this adapter can process the given video URL."""
        pass

    @abstractmethod
    def get_metadata(self, url: str) -> VideoMetadata:
        """Retrieve video metadata (title, duration, author, thumbnail, language)."""
        pass

    @abstractmethod
    def has_captions(self, url: str) -> bool:
        """Check whether readable captions or subtitles are accessible for this video."""
        pass

    @abstractmethod
    def extract_captions(
        self,
        url: str,
        preferred_languages: Optional[List[str]] = None,
    ) -> Optional[CaptionExtractionResult]:
        """
        Extract subtitles/captions without downloading full audio/video.
        Returns CaptionExtractionResult or None if captions are unavailable.
        """
        pass
