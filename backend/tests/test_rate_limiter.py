import pytest
from backend.app.security.rate_limiter import InMemoryRateLimiter


def test_in_memory_rate_limiter_allows_under_limit():
    limiter = InMemoryRateLimiter(max_requests=3, window_seconds=60)
    client_ip = "192.168.1.50"

    allowed1, _ = limiter.is_allowed(client_ip)
    allowed2, _ = limiter.is_allowed(client_ip)
    allowed3, _ = limiter.is_allowed(client_ip)

    assert allowed1 is True
    assert allowed2 is True
    assert allowed3 is True


def test_in_memory_rate_limiter_blocks_over_limit():
    limiter = InMemoryRateLimiter(max_requests=2, window_seconds=60)
    client_ip = "192.168.1.99"

    limiter.is_allowed(client_ip)
    limiter.is_allowed(client_ip)
    allowed3, retry_after = limiter.is_allowed(client_ip)

    assert allowed3 is False
    assert retry_after > 0


def test_in_memory_rate_limiter_isolates_different_ips():
    limiter = InMemoryRateLimiter(max_requests=1, window_seconds=60)
    ip_a = "10.0.0.1"
    ip_b = "10.0.0.2"

    allowed_a1, _ = limiter.is_allowed(ip_a)
    allowed_a2, _ = limiter.is_allowed(ip_a)
    allowed_b1, _ = limiter.is_allowed(ip_b)

    assert allowed_a1 is True
    assert allowed_a2 is False
    assert allowed_b1 is True
