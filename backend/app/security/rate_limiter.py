"""
Rate Limiting Middleware and Dependency for API Endpoints.
"""

import time
from typing import Dict, List, Tuple
from fastapi import Request, HTTPException, status


class RateLimitExceededException(HTTPException):
    def __init__(self, retry_after_seconds: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Please try again in {retry_after_seconds} seconds.",
            headers={"Retry-After": str(retry_after_seconds)},
        )


class InMemoryRateLimiter:
    """
    In-memory sliding window rate limiter per client IP.
    """

    def __init__(self, max_requests: int = 20, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.history: Dict[str, List[float]] = {}

    def is_allowed(self, client_ip: str) -> Tuple[bool, int]:
        """
        Checks if request is allowed for IP.
        Returns (is_allowed, retry_after_seconds).
        """
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old timestamps
        timestamps = self.history.get(client_ip, [])
        valid_timestamps = [ts for ts in timestamps if ts > window_start]

        if len(valid_timestamps) >= self.max_requests:
            oldest = valid_timestamps[0]
            retry_after = int(self.window_seconds - (now - oldest)) + 1
            self.history[client_ip] = valid_timestamps
            return False, max(1, retry_after)

        valid_timestamps.append(now)
        self.history[client_ip] = valid_timestamps
        return True, 0

    def reset(self):
        """Clears rate limit state (useful in tests)."""
        self.history.clear()


# Default limiter: 30 video submissions per hour per IP for MVP
global_rate_limiter = InMemoryRateLimiter(max_requests=30, window_seconds=3600)


def check_rate_limit(request: Request):
    """FastAPI dependency for rate limiting endpoints."""
    # Retrieve client IP
    client_ip = (
        request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        or (request.client.host if request.client else "127.0.0.1")
    )

    allowed, retry_after = global_rate_limiter.is_allowed(client_ip)
    if not allowed:
        raise RateLimitExceededException(retry_after_seconds=retry_after)
