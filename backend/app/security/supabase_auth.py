"""Supabase JWT authentication token verification and claim extraction.

Supports Supabase GoTrue Auth JWT verification with claims extraction
and dual-mode local JWT fallback.
"""

from __future__ import annotations

from typing import Any
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from app.security.exceptions import AuthenticationError


def verify_supabase_jwt(token: str, jwt_secret: str) -> dict[str, Any]:
    """Verify and decode a Supabase Auth access token.

    Args:
        token: The raw Bearer JWT string from the HTTP Authorization header.
        jwt_secret: The Supabase project JWT secret.

    Returns:
        dict: The decoded token claims containing 'sub', 'email', 'role', etc.

    Raises:
        AuthenticationError: If token is expired or signature is invalid.
    """
    if not token or not token.strip():
        raise AuthenticationError("Missing or empty authentication token")

    if not jwt_secret or not jwt_secret.strip():
        # If no secret is configured, perform unverified claim extraction for dev/test
        try:
            return jwt.decode(
                token,
                options={"verify_signature": False},
                algorithms=["HS256", "RS256"],
            )
        except InvalidTokenError as exc:
            raise AuthenticationError(f"Invalid token format: {exc}") from exc

    try:
        claims = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
        return claims
    except ExpiredSignatureError as exc:
        raise AuthenticationError("Authentication token has expired") from exc
    except InvalidTokenError as exc:
        raise AuthenticationError(f"Invalid authentication token: {exc}") from exc
