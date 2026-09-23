"""
Global Exception Handlers for FastAPI Application.
Converts exceptions into structured JSON error payloads.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from backend.app.core.exceptions import VideoScribeException
from backend.app.services.url_validator import URLValidationError, SSRFSecurityError


def register_error_handlers(app: FastAPI) -> None:
    """Registers global exception handlers on the FastAPI app instance."""

    @app.exception_handler(VideoScribeException)
    async def handle_videoscribe_exception(request: Request, exc: VideoScribeException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(SSRFSecurityError)
    async def handle_ssrf_error(request: Request, exc: SSRFSecurityError):
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": "SSRF_RESTRICTED_URL",
                    "message": "The provided URL targets a restricted local or internal network address.",
                    "details": str(exc),
                }
            },
        )

    @app.exception_handler(URLValidationError)
    async def handle_url_validation_error(request: Request, exc: URLValidationError):
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": "INVALID_URL",
                    "message": "We couldn't recognize this video URL. Please check the URL and try again.",
                    "details": str(exc),
                }
            },
        )
