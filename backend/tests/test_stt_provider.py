"""
Unit tests for Speech-to-Text providers and factory.
"""

from unittest.mock import MagicMock, patch
import pytest
from backend.app.providers.stt import get_stt_provider, MockSTTProvider, WhisperSTTProvider


def test_mock_stt_provider(tmp_path):
    """Verify MockSTTProvider returns structured segments and text."""
    dummy_audio = tmp_path / "test.mp3"
    dummy_audio.write_bytes(b"dummy audio binary data")

    provider = MockSTTProvider()
    result = provider.transcribe(str(dummy_audio), language="en")

    assert result.provider_name == "mock_stt"
    assert result.language == "en"
    assert len(result.segments) == 4
    assert result.segments[0].start_time == 0.0
    assert result.segments[0].end_time == 4.5
    assert "scalable data pipelines" in result.segments[0].text
    assert len(result.full_text) > 0


def test_stt_factory():
    """Verify get_stt_provider factory returns correct classes."""
    assert isinstance(get_stt_provider("mock"), MockSTTProvider)
    assert isinstance(get_stt_provider("openai"), WhisperSTTProvider)
    assert isinstance(get_stt_provider("unknown"), MockSTTProvider)


def test_whisper_provider_mocked_api(tmp_path):
    """Verify WhisperSTTProvider handles OpenAI verbose JSON response correctly."""
    dummy_audio = tmp_path / "speech.mp3"
    dummy_audio.write_bytes(b"audio stream")

    mock_openai_response = {
        "text": "Hello world from Whisper API.",
        "language": "en",
        "duration": 5.4,
        "segments": [
            {
                "id": 0,
                "start": 0.0,
                "end": 2.5,
                "text": "Hello world",
                "avg_logprob": -0.15,
            },
            {
                "id": 1,
                "start": 2.5,
                "end": 5.4,
                "text": "from Whisper API.",
                "avg_logprob": -0.12,
            },
        ],
    }

    mock_http_response = MagicMock()
    mock_http_response.status_code = 200
    mock_http_response.json.return_value = mock_openai_response

    provider = WhisperSTTProvider(api_key="sk-test-fake-key-12345")

    with patch("httpx.post", return_value=mock_http_response):
        result = provider.transcribe(str(dummy_audio))
        assert result.provider_name == "openai_whisper"
        assert result.language == "en"
        assert result.duration == 5.4
        assert len(result.segments) == 2
        assert result.segments[0].start_time == 0.0
        assert result.segments[0].end_time == 2.5
        assert result.segments[0].text == "Hello world"
