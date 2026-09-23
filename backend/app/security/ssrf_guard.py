"""
SSRF Protection & URL Sanitization Guard.
"""

import ipaddress
import socket
from urllib.parse import urlparse
from typing import List
from backend.app.services.url_validator import BLOCKED_NETWORKS, is_private_or_loopback_ip, SSRFSecurityError, URLValidationError


class SSRFGuard:
    """Security guard preventing Server-Side Request Forgery."""

    BLOCKED_HOSTNAMES = {
        "localhost",
        "127.0.0.1",
        "::1",
        "0.0.0.0",
        "169.254.169.254",  # AWS instance metadata
        "metadata.google.internal",  # GCP metadata
        "169.254.169.254.nip.io",
        "127.0.0.1.nip.io",
    }

    ALLOWED_SCHEMES = {"http", "https"}

    @classmethod
    def validate_safe_target(cls, url: str, resolve_dns: bool = True) -> str:
        """
        Thoroughly inspects a URL and verifies that its hostname/resolved IP
        does not point to internal network interfaces, loopback, or metadata services.
        """
        if not url or not isinstance(url, str):
            raise URLValidationError("Target URL cannot be empty.")

        cleaned = url.strip()
        if "://" in cleaned:
            scheme = cleaned.split("://", 1)[0].lower()
            if scheme not in cls.ALLOWED_SCHEMES:
                raise URLValidationError(f"Invalid URL scheme: '{scheme}'.")
        else:
            cleaned = "https://" + cleaned

        parsed = urlparse(cleaned)
        hostname = parsed.hostname
        if not hostname:
            raise URLValidationError("Invalid URL: missing hostname.")

        hostname_lower = hostname.lower()

        if hostname_lower in cls.BLOCKED_HOSTNAMES:
            raise SSRFSecurityError(f"Access to restricted hostname '{hostname}' is blocked.")

        # Check direct IP
        try:
            ip_obj = ipaddress.ip_address(hostname_lower)
            if is_private_or_loopback_ip(str(ip_obj)):
                raise SSRFSecurityError(f"Access to private IP address '{hostname}' is blocked.")
        except ValueError:
            pass  # Domain name

        # Resolve DNS
        if resolve_dns:
            try:
                addr_info = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
                for res in addr_info:
                    resolved_ip = res[4][0]
                    if is_private_or_loopback_ip(resolved_ip):
                        raise SSRFSecurityError(
                            f"Resolved host '{hostname}' pointed to restricted IP '{resolved_ip}'."
                        )
            except socket.gaierror:
                pass  # DNS failed, will fail downstream gracefully

        return cleaned
