"""
Unit tests for AudioExtractor service with mocked ffmpeg and yt-dlp.
"""

import os
from unittest.mock import MagicMock, patch
import pytest
from backend.app.services.audio_extractor import AudioExtractor, AudioExtractionError


@pytest.fixture
def extractor(tmp_path):
    return AudioExtractor(temp_dir=str(tmp_path))


def test_extract_audio_from_file_success(extractor, tmp_path):
    """Verify ffmpeg audio extraction command invocation."""
    input_video = tmp_path / "sample.mp4"
    input_video.write_bytes(b"dummy video data")

    expected_output = tmp_path / "custom_audio.mp3"

    with patch("subprocess.run") as mock_run, patch("os.path.exists") as mock_exists, patch("os.path.getsize") as mock_size:
        mock_run.return_value = MagicMock(returncode=0)
        mock_exists.return_value = True
        mock_size.return_value = 1024

        output = extractor.extract_audio_from_file(str(input_video), output_filename="custom_audio.mp3")
        assert output.endswith("custom_audio.mp3")
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "ffmpeg"
        assert "-ar" in cmd
        assert "16000" in cmd
        assert "-ac" in cmd
        assert "1" in cmd


def test_extract_audio_missing_input_file(extractor):
    """Verify error raised when input file does not exist."""
    with pytest.raises(AudioExtractionError):
        extractor.extract_audio_from_file("/non/existent/path.mp4")


def test_cleanup_file(extractor, tmp_path):
    """Verify safe cleanup deletes existing temp file."""
    test_file = tmp_path / "temp_audio.mp3"
    test_file.write_bytes(b"123")
    assert test_file.exists()

    extractor.cleanup_file(str(test_file))
    assert not test_file.exists()
