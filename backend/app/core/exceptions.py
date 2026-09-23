"""
Application Custom Exceptions with User-Facing Error Messages.
Adheres strictly to PRD Section 15 Error Handling specifications.
"""

from typing import Optional


class VideoScribeException(Exception):
    """Base exception for application errors."""
    def __init__(self, message: str, code: str, status_code: int = 400, details: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class InvalidUrlException(VideoScribeException):
    """Raised when URL is malformed or invalid."""
    def __init__(self, details: Optional[str] = None):
        super().__init__(
            message="We couldn't recognize this video URL. Please check the URL and try again.",
            code="INVALID_URL",
            status_code=400,
            details=details,
        )


class UnsupportedPlatformException(VideoScribeException):
    """Raised when URL belongs to an unsupported platform."""
    def __init__(self, details: Optional[str] = None):
        super().__init__(
            message="This platform isn't currently supported. Try uploading the video instead.",
            code="UNSUPPORTED_PLATFORM",
            status_code=400,
            details=details,
        )


class CaptionsUnavailableException(VideoScribeException):
    """Raised when captions cannot be extracted and audio cannot be retrieved."""
    def __init__(self, details: Optional[str] = None):
        super().__init__(
            message="Captions aren't available for this video. If you own or can upload the video, upload it here to generate a transcript.",
            code="CAPTIONS_UNAVAILABLE",
            status_code=404,
            details=details,
        )


class PrivateVideoException(VideoScribeException):
    """Raised when video is restricted or private."""
    def __init__(self, details: Optional[str] = None):
        super().__init__(
            message="We can't access this private video. Please provide an accessible video or upload the file.",
            code="PRIVATE_VIDEO",
            status_code=403,
            details=details,
        )


class ProcessingFailureException(VideoScribeException):
    """Raised when unexpected processing pipeline failure occurs."""
    def __init__(self, details: Optional[str] = None):
        super().__init__(
            message="We couldn't process this video. Please try again or upload the video directly.",
            code="PROCESSING_FAILURE",
            status_code=500,
            details=details,
        )


class VideoNotFoundException(VideoScribeException):
    """Raised when video ID is not found."""
    def __init__(self, video_id: str):
        super().__init__(
            message=f"Video '{video_id}' not found.",
            code="VIDEO_NOT_FOUND",
            status_code=404,
        )


class JobNotFoundException(VideoScribeException):
    """Raised when job ID is not found."""
    def __init__(self, job_id: str):
        super().__init__(
            message=f"Transcription job '{job_id}' not found.",
            code="JOB_NOT_FOUND",
            status_code=404,
        )


class TranscriptNotFoundException(VideoScribeException):
    """Raised when transcript ID is not found."""
    def __init__(self, transcript_id: str):
        super().__init__(
            message=f"Transcript '{transcript_id}' not found.",
            code="TRANSCRIPT_NOT_FOUND",
            status_code=404,
        )
