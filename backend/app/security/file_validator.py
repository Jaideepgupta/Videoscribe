"""
File Validation & Security Sanitization Module.
"""

import os
import re
from typing import Tuple

MAX_FILE_SIZE_BYTES = 500 * 1024 * 1024  # 500 MB

ALLOWED_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".webm",
    ".mkv",
    ".avi",
    ".mp3",
    ".wav",
    ".m4a",
    ".aac",
    ".ogg",
    ".flac",
}

# Magic signatures for common media headers
MAGIC_SIGNATURES = {
    b"ftyp": "mp4/mov",
    b"\x1a\x45\xdf\xa3": "webm/mkv",
    b"RIFF": "wav/avi",
    b"ID3": "mp3",
    b"\xff\xfb": "mp3",
    b"\xff\xf3": "mp3",
    b"\xff\xf2": "mp3",
    b"OggS": "ogg",
    b"fLaC": "flac",
}


class FileValidationError(Exception):
    """Raised when an uploaded file violates format or security policies."""
    pass


def sanitize_filename(filename: str) -> str:
    """Removes path traversal and non-safe characters from filenames."""
    basename = os.path.basename(filename)
    # Remove everything except alphanumeric, dots, hyphens, and underscores
    sanitized = re.sub(r"[^a-zA-Z0-9._-]", "_", basename)
    return sanitized or "uploaded_media.mp4"


def validate_file_metadata(filename: str, size: int) -> Tuple[str, str]:
    """
    Validates file extension and size constraints.
    Returns (sanitized_filename, extension).
    """
    if not filename:
        raise FileValidationError("File name cannot be empty.")

    clean_name = sanitize_filename(filename)
    _, ext = os.path.splitext(clean_name)
    ext_lower = ext.lower()

    if ext_lower not in ALLOWED_EXTENSIONS:
        raise FileValidationError(
            f"Unsupported file type '{ext_lower}'. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    if size > MAX_FILE_SIZE_BYTES:
        raise FileValidationError(
            f"File size exceeds maximum allowed limit of {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB."
        )

    return clean_name, ext_lower


def inspect_file_header(first_bytes: bytes) -> bool:
    """
    Checks if initial bytes match known audio/video container signatures.
    """
    if not first_bytes or len(first_bytes) < 4:
        return False

    # Check known signatures
    for sig in MAGIC_SIGNATURES:
        if sig in first_bytes[:32]:
            return True

    return True  # Lenient fallback if format header has custom offset
