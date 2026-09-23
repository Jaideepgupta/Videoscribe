import pytest
from backend.app.security.ssrf_guard import SSRFGuard
from backend.app.services.url_validator import SSRFSecurityError, URLValidationError


def test_ssrf_guard_valid_urls():
    valid = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    result = SSRFGuard.validate_safe_target(valid, resolve_dns=False)
    assert result == valid


def test_ssrf_guard_blocks_localhost_and_metadata():
    with pytest.raises(SSRFSecurityError):
        SSRFGuard.validate_safe_target("http://localhost:8000/api", resolve_dns=False)

    with pytest.raises(SSRFSecurityError):
        SSRFGuard.validate_safe_target("http://127.0.0.1:5000", resolve_dns=False)

    with pytest.raises(SSRFSecurityError):
        SSRFGuard.validate_safe_target("http://169.254.169.254/latest/meta-data/", resolve_dns=False)

    with pytest.raises(SSRFSecurityError):
        SSRFGuard.validate_safe_target("http://metadata.google.internal/computeMetadata/v1/", resolve_dns=False)


def test_ssrf_guard_blocks_disallowed_schemes():
    with pytest.raises(URLValidationError):
        SSRFGuard.validate_safe_target("ftp://ftp.example.com/file.mp4", resolve_dns=False)

    with pytest.raises(URLValidationError):
        SSRFGuard.validate_safe_target("file:///etc/passwd", resolve_dns=False)
