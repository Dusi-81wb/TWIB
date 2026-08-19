"""Authentication and security constants.

Centralizes default algorithm names, token types, expiry durations, and header
constants used across the authentication foundation.
"""

from __future__ import annotations

DEFAULT_JWT_ALGORITHM: str = "HS256"
DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

TOKEN_TYPE_BEARER: str = "bearer"  # noqa: S105
TOKEN_TYPE_ACCESS: str = "access"  # noqa: S105

HEADER_AUTHORIZATION: str = "Authorization"
HEADER_PREFIX_BEARER: str = "Bearer"
