"""
Unit tests for configuration validation and environment loading.
"""

import os
import pytest
from backend.app.config import Settings


def test_default_settings():
    """Verify default settings instantiation."""
    settings = Settings()
    assert settings.PROJECT_NAME == "Video2Content"
    assert settings.ENVIRONMENT in ["development", "testing", "production"]
    assert settings.MAX_UPLOAD_SIZE_MB == 500
    assert settings.max_upload_size_bytes == 500 * 1024 * 1024
    assert settings.STT_PROVIDER in ["mock", "openai", "faster_whisper"]


def test_cors_parsing_comma_separated():
    """Verify comma-separated CORS string parsing."""
    settings = Settings(BACKEND_CORS_ORIGINS="http://localhost:3000,https://app.example.com")
    assert "http://localhost:3000" in settings.BACKEND_CORS_ORIGINS
    assert "https://app.example.com" in settings.BACKEND_CORS_ORIGINS
    assert len(settings.BACKEND_CORS_ORIGINS) == 2


def test_cors_parsing_list():
    """Verify direct list parsing for CORS."""
    origins = ["http://localhost:3000", "http://localhost:8000"]
    settings = Settings(BACKEND_CORS_ORIGINS=origins)
    assert settings.BACKEND_CORS_ORIGINS == origins
