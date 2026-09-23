"""
Speech-to-Text Providers Factory.
"""

from typing import Optional
from backend.app.config import settings
from backend.app.providers.stt.base import BaseSTTProvider
from backend.app.providers.stt.mock_provider import MockSTTProvider
from backend.app.providers.stt.whisper_provider import WhisperSTTProvider


def get_stt_provider(provider_name: Optional[str] = None) -> BaseSTTProvider:
    """
    Factory function returning the configured STT provider instance.
    Defaults to settings.STT_PROVIDER.
    """
    provider = (provider_name or settings.STT_PROVIDER).lower()

    if provider == "openai":
        return WhisperSTTProvider()
    elif provider in ("mock", "test"):
        return MockSTTProvider()
    else:
        # Default fallback to mock provider for safe offline development
        return MockSTTProvider()


__all__ = [
    "BaseSTTProvider",
    "MockSTTProvider",
    "WhisperSTTProvider",
    "get_stt_provider",
]
