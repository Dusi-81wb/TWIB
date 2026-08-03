"""Refresh token generation and secure hashing utilities.

Provides secure random refresh token generation and SHA-256 token hashing
so plaintext refresh tokens are never persisted.
"""

from __future__ import annotations

import hashlib
import secrets


def generate_refresh_token() -> tuple[str, str]:
    """Generate a new secure random refresh token and its SHA-256 hash.

    Returns:
        A tuple of (raw_refresh_token, hashed_refresh_token).
    """
    raw_token = secrets.token_urlsafe(32)
    hashed_token = hash_refresh_token(raw_token)
    return raw_token, hashed_token


def hash_refresh_token(raw_token: str) -> str:
    """Compute the SHA-256 hash of a raw refresh token string.

    Args:
        raw_token: Plaintext refresh token string.

    Returns:
        Hexadecimal SHA-256 hash digest string.
    """
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def verify_refresh_token_hash(raw_token: str, expected_hash: str) -> bool:
    """Verify a raw refresh token against its expected SHA-256 hash digest.

    Args:
        raw_token: Plaintext refresh token to verify.
        expected_hash: Stored SHA-256 hash string.

    Returns:
        True if the computed hash matches expected_hash, False otherwise.
    """
    computed = hash_refresh_token(raw_token)
    return secrets.compare_digest(computed, expected_hash)
