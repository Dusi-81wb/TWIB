"""API Key domain exceptions.

Defines custom exceptions for API key validation and state errors.
"""

from __future__ import annotations

from app.domain.exceptions import DomainException


class ApiKeyException(DomainException):
    """Base exception for API key domain errors."""


class InvalidApiKeyError(ApiKeyException):
    """Raised when an API key is invalid, malformed, or not found."""


class ApiKeyExpiredError(ApiKeyException):
    """Raised when an API key has passed its expiration time."""


class ApiKeyRevokedError(ApiKeyException):
    """Raised when an API key has been revoked."""
