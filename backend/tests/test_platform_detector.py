"""
Unit tests for URL validation and PlatformDetector.
"""

import pytest
from backend.app.models.video import PlatformType
from backend.app.providers.platform_detector import PlatformDetector
from backend.app.services.url_validator import (
    validate_url,
    URLValidationError,
    SSRFSecurityError,
)


def test_ssrf_protection_blocked_hosts():
    """Verify SSRF protection blocks localhost, private IPs, and metadata services."""
    blocked_urls = [
        "http://localhost:8000/video.mp4",
        "http://127.0.0.1/video.mp4",
        "http://10.0.0.5/stream",
        "http://192.168.1.100/video",
        "http://172.16.0.2/file.mp4",
        "http://169.254.169.254/latest/meta-data/",
        "http://0.0.0.0/test",
    ]
    for url in blocked_urls:
        with pytest.raises(SSRFSecurityError):
            validate_url(url)


def test_invalid_urls():
    """Verify invalid and malformed URLs raise URLValidationError."""
    invalid_urls = [
        "",
        "   ",
        "ftp://example.com/video.mp4",
        "file:///etc/passwd",
    ]
    for url in invalid_urls:
        with pytest.raises(URLValidationError):
            validate_url(url)


def test_youtube_url_variations():
    """Verify extraction of YouTube IDs across various link structures."""
    test_cases = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://m.youtube.com/watch?v=dQw4w9WgXcQ&feature=shared", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/live/dQw4w9WgXcQ?si=123", "dQw4w9WgXcQ"),
    ]

    for url, expected_id in test_cases:
        platform, video_id, canonical = PlatformDetector.detect(url)
        assert platform == PlatformType.YOUTUBE
        assert video_id == expected_id
        assert canonical == f"https://www.youtube.com/watch?v={expected_id}"


def test_vimeo_detection():
    """Verify Vimeo URL detection."""
    url = "https://vimeo.com/76979871"
    platform, video_id, canonical = PlatformDetector.detect(url)
    assert platform == PlatformType.VIMEO
    assert video_id == "76979871"


def test_direct_media_detection():
    """Verify direct audio/video URL detection."""
    url = "https://example.com/media/lecture_01.mp4"
    platform, video_id, canonical = PlatformDetector.detect(url)
    assert platform == PlatformType.DIRECT
    assert video_id is None
