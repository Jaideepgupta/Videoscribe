"""
Platform Ingestion Providers Package.
"""

from backend.app.providers.base import BasePlatformAdapter
from backend.app.providers.platform_detector import PlatformDetector
from backend.app.providers.youtube import YouTubeAdapter, youtube_adapter

__all__ = [
    "BasePlatformAdapter",
    "PlatformDetector",
    "YouTubeAdapter",
    "youtube_adapter",
]
