"""
Unit tests for YouTubeAdapter with mocked youtube_transcript_api and yt_dlp.
"""

from unittest.mock import MagicMock, patch
import pytest
from youtube_transcript_api import TranscriptsDisabled
from backend.app.models.video import PlatformType
from backend.app.providers.youtube import YouTubeAdapter


@pytest.fixture
def youtube_adapter():
    return YouTubeAdapter()


def test_youtube_metadata_mocked(youtube_adapter):
    """Verify metadata extraction with mocked yt-dlp."""
    mock_info = {
        "id": "dQw4w9WgXcQ",
        "title": "Rick Astley - Never Gonna Give You Up",
        "duration": 212,
        "uploader": "RickAstleyVEVO",
        "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
        "description": "The official video...",
        "language": "en",
        "subtitles": {"en": [{"ext": "vtt"}]},
    }

    mock_ydl = MagicMock()
    mock_ydl.__enter__.return_value.extract_info.return_value = mock_info

    with patch("yt_dlp.YoutubeDL", return_value=mock_ydl):
        meta = youtube_adapter.get_metadata("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert meta.title == "Rick Astley - Never Gonna Give You Up"
        assert meta.duration == 212
        assert meta.author == "RickAstleyVEVO"
        assert meta.platform == PlatformType.YOUTUBE
        assert meta.has_captions is True


def test_youtube_caption_extraction_success(youtube_adapter):
    """Verify caption extraction with mocked transcript retrieval."""
    mock_transcript = MagicMock()
    mock_transcript.language_code = "en"
    mock_transcript.is_generated = False
    mock_transcript.fetch.return_value = [
        {"start": 1.2, "duration": 3.0, "text": "Welcome to the tutorial."},
        {"start": 4.5, "duration": 2.5, "text": "Today we discuss database design."},
    ]

    mock_transcript_list = MagicMock()
    mock_transcript_list.find_manually_created_transcript.return_value = mock_transcript

    with patch.object(youtube_adapter, "_get_transcript_list", return_value=mock_transcript_list):
        result = youtube_adapter.extract_captions("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert result is not None
        assert result.language == "en"
        assert len(result.segments) == 2
        assert result.segments[0].text == "Welcome to the tutorial."
        assert result.segments[0].start_time == 1.2
        assert result.segments[0].end_time == 4.2
        assert result.segments[1].text == "Today we discuss database design."


def test_youtube_caption_disabled(youtube_adapter):
    """Verify graceful return of None when captions are disabled on video."""
    with patch.object(youtube_adapter, "_get_transcript_list", side_effect=TranscriptsDisabled("dQw4w9WgXcQ")):
        result = youtube_adapter.extract_captions("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert result is None
        assert youtube_adapter.has_captions("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is False
