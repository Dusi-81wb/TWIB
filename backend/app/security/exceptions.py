"""Security and authentication exceptions.

Defines custom exception hierarchy for password hashing, token validation,
and authentication failures.
"""

from __future__ import annotations


class SecurityError(Exception):
    """Base exception for all security and authentication errors."""


class AuthenticationError(SecurityError):
    """Raised when an authentication operation fails."""


class InvalidTokenError(AuthenticationError):
    """Raised when a JWT token is malformed, corrupted, or signature is invalid."""


class TokenExpiredError(InvalidTokenError):
    """Raised when a JWT token timestamp has expired."""


class InvalidPasswordError(AuthenticationError):
    """Raised when password verification fails against a stored hash."""
