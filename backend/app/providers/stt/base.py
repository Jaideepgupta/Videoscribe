"""
Abstract Base Class for Speech-to-Text Providers.
"""

from abc import ABC, abstractmethod
from typing import Optional
from backend.app.schemas.stt import STTResult


class BaseSTTProvider(ABC):
    """Abstract interface for Speech-to-Text providers."""

    @abstractmethod
    def transcribe(self, audio_file_path: str, language: Optional[str] = None) -> STTResult:
        """
        Transcribes a local audio file and returns structured STTResult.
        """
        pass
