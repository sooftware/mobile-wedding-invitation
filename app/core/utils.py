"""Common Utility Functions.

This module provides shared utility functions used across the application:
- Password hashing using SHA-256
- Client IP address extraction (with proxy support)
- Other common helper functions

These utilities are designed to be stateless and reusable throughout
the application without side effects.
"""

import hashlib
from fastapi import Request


def hash_password(password: str) -> str:
    """Generate SHA-256 hash of password.

    Args:
        password (str): Plain text password to hash

    Returns:
        str: Hexadecimal SHA-256 hash of the password

    Example:
        >>> hash_password("secret123")
        '2bb80d537b1da3e38bd30361aa855686bde0eacd7162fef6a25fe97bf527a25b'
    """
    return hashlib.sha256(password.encode()).hexdigest()


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request with proxy support.

    Checks headers in the following order:
    1. X-Forwarded-For (proxy/load balancer)
    2. X-Real-IP (alternative proxy header)
    3. Direct client connection

    Args:
        request (Request): FastAPI Request object

    Returns:
        str: Client IP address or "unknown" if unavailable

    Note:
        When behind a proxy, X-Forwarded-For may contain multiple IPs.
        The first IP is returned as it represents the original client.
    """
    # X-Forwarded-For 헤더 확인 (프록시/로드밸런서 사용 시)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    # X-Real-IP 헤더 확인
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # 직접 연결된 클라이언트 IP
    return request.client.host if request.client else "unknown"