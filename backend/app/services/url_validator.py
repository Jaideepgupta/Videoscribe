"""
URL Validation and SSRF Guard Service.
"""

import ipaddress
import re
import socket
from urllib.parse import urlparse
from typing import Tuple


class URLValidationError(Exception):
    """Raised when a URL is malformed or violates security policies."""
    pass


class SSRFSecurityError(URLValidationError):
    """Raised when a URL targets a private/internal IP address."""
    pass


# Disallowed IP networks for SSRF protection
BLOCKED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),       # Link-local / AWS metadata (169.254.169.254)
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("198.18.0.0/15"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
    ipaddress.ip_network("224.0.0.0/4"),         # Multicast
    ipaddress.ip_network("240.0.0.0/4"),         # Reserved
    ipaddress.ip_network("255.255.255.255/32"),
    # IPv6
    ipaddress.ip_network("::1/128"),             # IPv6 Loopback
    ipaddress.ip_network("fc00::/7"),            # Unique local
    ipaddress.ip_network("fe80::/10"),           # Link-local
]


def is_private_or_loopback_ip(ip_str: str) -> bool:
    """Check if an IP string belongs to private, loopback, or reserved address spaces."""
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved:
            return True
        for network in BLOCKED_NETWORKS:
            if ip_obj in network:
                return True
        return False
    except ValueError:
        return True


def validate_url(url: str, check_dns: bool = False) -> str:
    """
    Validates a URL for format, allowed schemes, and SSRF restrictions.
    Returns the sanitized URL or raises URLValidationError / SSRFSecurityError.
    """
    if not url or not isinstance(url, str):
        raise URLValidationError("URL cannot be empty.")

    cleaned_url = url.strip()
    if not cleaned_url:
        raise URLValidationError("URL cannot be empty.")

    # If scheme is present (e.g. ftp://, file://, http://), check it directly
    if "://" in cleaned_url:
        scheme = cleaned_url.split("://", 1)[0].lower()
        if scheme not in ("http", "https"):
            raise URLValidationError(f"Unsupported URL scheme: '{scheme}'. Only HTTP/HTTPS allowed.")
    else:
        cleaned_url = "https://" + cleaned_url

    parsed = urlparse(cleaned_url)

    # 1. Scheme Check
    if parsed.scheme.lower() not in ("http", "https"):
        raise URLValidationError(f"Unsupported URL scheme: '{parsed.scheme}'. Only HTTP/HTTPS allowed.")

    # 2. Hostname Check
    hostname = parsed.hostname
    if not hostname:
        raise URLValidationError("URL must include a valid hostname.")

    hostname_lower = hostname.lower()

    # Block direct localhost strings
    if hostname_lower in ("localhost", "127.0.0.1", "::1", "0.0.0.0", "metadata.google.internal"):
        raise SSRFSecurityError(f"Access to host '{hostname}' is restricted.")

    # Check if hostname is an IP address
    try:
        ip_obj = ipaddress.ip_address(hostname_lower)
        if is_private_or_loopback_ip(str(ip_obj)):
            raise SSRFSecurityError(f"Access to private IP '{hostname}' is restricted.")
    except ValueError:
        pass  # Not an IP string, hostname is domain name

    # 3. Optional DNS resolution check for SSRF
    if check_dns:
        try:
            addr_info = socket.getaddrinfo(hostname, None)
            for item in addr_info:
                ip_resolved = item[4][0]
                if is_private_or_loopback_ip(ip_resolved):
                    raise SSRFSecurityError(f"Resolved IP '{ip_resolved}' for host '{hostname}' is restricted.")
        except socket.gaierror:
            pass  # DNS resolution failure will be handled gracefully during network retrieval

    return cleaned_url
