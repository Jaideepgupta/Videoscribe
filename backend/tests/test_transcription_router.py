"""
Unit tests for TranscriptionRouter decision engine and cost optimization.
"""

from unittest.mock import MagicMock, patch
import pytest
from backend.app.models.video import PlatformType
from backend.app.providers.stt.mock_provider import MockSTTProvider
from backend.app.schemas.provider import CaptionExtractionResult, RawCaptionSegment, VideoMetadata
from backend.app.services.transcription_router import TranscriptionRouter


@pytest.fixture
def router():
    mock_stt = MockSTTProvider()
    mock_extractor = MagicMock()
    return TranscriptionRouter(stt_provider=mock_stt, extractor=mock_extractor)


def test_caption_first_optimization_bypass(router):
    """Verify that videos with native captions bypass STT extraction completely."""
    mock_captions = CaptionExtractionResult(
        language="en",
        is_generated=False,
        segments=[
            RawCaptionSegment(start_time=0.0, end_time=3.0, duration=3.0, text="Intro to Python."),
            RawCaptionSegment(start_time=3.0, end_time=7.0, duration=4.0, text="Let's write clean functions."),
        ],
        raw_full_text="Intro to Python. Let's write clean functions.",
    )

    mock_metadata = VideoMetadata(
        title="Python Fast Track",
        duration=120,
        platform=PlatformType.YOUTUBE,
        canonical_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        has_captions=True,
    )

    with patch("backend.app.providers.youtube.youtube_adapter.can_handle", return_value=True), \
         patch("backend.app.providers.youtube.youtube_adapter.get_metadata", return_value=mock_metadata), \
         patch("backend.app.providers.youtube.youtube_adapter.extract_captions", return_value=mock_captions):

        payload = router.process_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

        assert payload.source_type == "captions"
        assert payload.provider_name == "youtube_captions"
        assert len(payload.segments) == 2
        assert payload.segments[0].text == "Intro to Python."
        # Audio extractor should NOT have been called
        router.extractor.extract_audio_from_url.assert_not_called()


def test_stt_fallback_when_captions_unavailable(router, tmp_path):
    """Verify fallback to audio extraction and STT when captions are absent."""
    dummy_audio_file = tmp_path / "extracted_audio.mp3"
    dummy_audio_file.write_bytes(b"audio binary")
    router.extractor.extract_audio_from_url.return_value = str(dummy_audio_file)

    with patch("backend.app.providers.youtube.youtube_adapter.can_handle", return_value=True), \
         patch("backend.app.providers.youtube.youtube_adapter.get_metadata", return_value=VideoMetadata(
             title="No Captions Video", duration=60, canonical_url="https://www.youtube.com/watch?v=123", has_captions=False
         )), \
         patch("backend.app.providers.youtube.youtube_adapter.extract_captions", return_value=None):

        payload = router.process_url("https://www.youtube.com/watch?v=123")

        assert payload.source_type == "stt_transcription"
        assert payload.provider_name == "mock_stt"
        assert len(payload.segments) == 4
        router.extractor.extract_audio_from_url.assert_called_once()
        router.extractor.cleanup_file.assert_called_once_with(str(dummy_audio_file))


def test_process_uploaded_video_file(router, tmp_path):
    """Verify uploaded video files are routed through FFmpeg extractor and STT."""
    uploaded_video = tmp_path / "recording.mp4"
    uploaded_video.write_bytes(b"video mp4 bytes")

    extracted_mp3 = tmp_path / "extracted.mp3"
    extracted_mp3.write_bytes(b"audio mp3 bytes")
    router.extractor.extract_audio_from_file.return_value = str(extracted_mp3)

    payload = router.process_uploaded_file(str(uploaded_video), filename="recording.mp4")

    assert payload.platform == PlatformType.UPLOAD
    assert payload.source_type == "stt_transcription"
    assert payload.provider_name == "mock_stt"
    assert len(payload.segments) == 4
    router.extractor.extract_audio_from_file.assert_called_once_with(str(uploaded_video))
    router.extractor.cleanup_file.assert_called_once_with(str(extracted_mp3))
