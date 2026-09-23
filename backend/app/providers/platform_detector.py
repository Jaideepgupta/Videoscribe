"""
Platform Detection Engine.
Identifies video platform provider from URL and extracts canonical identifiers.
"""

import re
from urllib.parse import parse_qs, urlparse
from typing import Optional, Tuple
from backend.app.models.video import PlatformType
from backend.app.services.url_validator import validate_url


class PlatformDetector:
    """Detects video platform from URL and extracts platform-specific video IDs."""

    # Regex patterns for YouTube video IDs (11 alphanumeric, hyphen, underscore chars)
    YOUTUBE_DOMAINS = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be"}
    VIMEO_DOMAINS = {"vimeo.com", "www.vimeo.com", "player.vimeo.com"}

    @classmethod
    def extract_youtube_id(cls, url: str) -> Optional[str]:
        """
        Extracts 11-character YouTube video ID from various YouTube URL formats:
        - https://www.youtube.com/watch?v=dQw4w9WgXcQ
        - https://youtu.be/dQw4w9WgXcQ
        - https://www.youtube.com/embed/dQw4w9WgXcQ
        - https://www.youtube.com/shorts/dQw4w9WgXcQ
        - https://www.youtube.com/v/dQw4w9WgXcQ
        - https://www.youtube.com/live/dQw4w9WgXcQ
        """
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()

        if hostname not in cls.YOUTUBE_DOMAINS:
            return None

        # Format: youtu.be/ID
        if hostname == "youtu.be":
            path_parts = parsed.path.strip("/").split("/")
            if path_parts and len(path_parts[0]) == 11:
                return path_parts[0]

        # Format: youtube.com/watch?v=ID
        if "watch" in parsed.path:
            query_params = parse_qs(parsed.query)
            if "v" in query_params and query_params["v"]:
                candidate = query_params["v"][0]
                if len(candidate) == 11:
                    return candidate

        # Format: youtube.com/embed/ID, youtube.com/shorts/ID, youtube.com/v/ID, youtube.com/live/ID
        for prefix in ("/embed/", "/shorts/", "/v/", "/live/"):
            if prefix in parsed.path:
                parts = parsed.path.split(prefix)
                if len(parts) > 1:
                    candidate = parts[1].split("/")[0].split("?")[0]
                    if len(candidate) == 11:
                        return candidate

        # Generic 11-char regex search as fallback
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
        if match:
            return match.group(1)

        return None

    @classmethod
    def extract_vimeo_id(cls, url: str) -> Optional[str]:
        """Extracts numeric Vimeo video ID."""
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()
        if hostname in cls.VIMEO_DOMAINS:
            match = re.search(r"(?:channels\/(?:\w+\/)?|groups\/[^\/]*\/videos\/|album\/(?:\d+\/)?video\/|video\/|)(\d+)", parsed.path)
            if match:
                return match.group(1)
        return None

    @classmethod
    def detect(cls, raw_url: str) -> Tuple[PlatformType, Optional[str], str]:
        """
        Detects platform type, video ID, and normalized URL.
        Returns (PlatformType, video_id, normalized_url).
        """
        clean_url = validate_url(raw_url)

        # Check YouTube
        yt_id = cls.extract_youtube_id(clean_url)
        if yt_id:
            canonical_url = f"https://www.youtube.com/watch?v={yt_id}"
            return PlatformType.YOUTUBE, yt_id, canonical_url

        # Check Vimeo
        vimeo_id = cls.extract_vimeo_id(clean_url)
        if vimeo_id:
            return PlatformType.VIMEO, vimeo_id, f"https://vimeo.com/{vimeo_id}"

        # Check Direct media files
        parsed = urlparse(clean_url)
        path_lower = parsed.path.lower()
        if any(path_lower.endswith(ext) for ext in (".mp4", ".mov", ".webm", ".mkv", ".mp3", ".wav", ".m4a")):
            return PlatformType.DIRECT, None, clean_url

        return PlatformType.OTHER, None, clean_url
