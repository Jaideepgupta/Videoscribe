import pytest
from backend.app.security.file_validator import (
    validate_file_metadata,
    sanitize_filename,
    inspect_file_header,
    FileValidationError,
    MAX_FILE_SIZE_BYTES,
)


def test_sanitize_filename():
    assert sanitize_filename("../../../etc/passwd.mp4") == "passwd.mp4"
    assert sanitize_filename("my video #1 (2026).mp4") == "my_video__1__2026_.mp4"
    assert sanitize_filename("") == "uploaded_media.mp4"


def test_validate_file_metadata_valid():
    filename, ext = validate_file_metadata("sample_recording.mp4", 1024 * 1024)
    assert filename == "sample_recording.mp4"
    assert ext == ".mp4"


def test_validate_file_metadata_invalid_extension():
    with pytest.raises(FileValidationError, match="Unsupported file type"):
        validate_file_metadata("malicious_script.exe", 1024)

    with pytest.raises(FileValidationError, match="Unsupported file type"):
        validate_file_metadata("document.pdf", 1024)


def test_validate_file_metadata_exceeds_size():
    with pytest.raises(FileValidationError, match="File size exceeds"):
        validate_file_metadata("huge_video.mp4", MAX_FILE_SIZE_BYTES + 100)


def test_inspect_file_header():
    # MP4 ftyp header
    assert inspect_file_header(b"\x00\x00\x00\x20ftypmp42\x00\x00\x00\x00") is True
    # WebM EBML header
    assert inspect_file_header(b"\x1a\x45\xdf\xa3\x93\x42\x82\x88matroska") is True
    # MP3 ID3 header
    assert inspect_file_header(b"ID3\x04\x00\x00\x00\x00\x00\x23") is True
    # Too short
    assert inspect_file_header(b"ab") is False
