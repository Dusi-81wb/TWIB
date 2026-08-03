"""LLM Provider exception hierarchy.

Defines provider-independent exception types for LLM integration. Outer
layers can catch these exceptions without depending on provider SDKs.
"""

from __future__ import annotations

from typing import Any

from fastapi import status

from app.core.error_codes import (
    INTERNAL_SERVER_ERROR,
    RATE_LIMIT_EXCEEDED,
    RESOURCE_NOT_FOUND,
    SERVICE_UNAVAILABLE,
    UNAUTHORIZED,
    VALIDATION_ERROR,
)
from app.core.exceptions import TWIBException


class LLMProviderError(TWIBException):
    """Base exception for all LLM provider errors."""

    error_code: str = INTERNAL_SERVER_ERROR
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self,
        message: str,
        *,
        provider: str = "unknown",
        model: str | None = None,
        details: dict[str, Any] | None = None,
        error_code: str | None = None,
        status_code: int | None = None,
    ) -> None:
        """Initialize LLMProviderError with provider context.

        Args:
            message: Human-readable error description.
            provider: Name of the LLM provider (e.g. 'openai', 'ollama').
            model: Name of the target model if applicable.
            details: Optional structured information about the error.
            error_code: Optional override error code.
            status_code: Optional override HTTP status code.
        """
        extra_details = details or {}
        extra_details["provider"] = provider
        if model:
            extra_details["model"] = model
        super().__init__(
            message,
            details=extra_details,
            error_code=error_code,
            status_code=status_code,
        )
        self.provider = provider
        self.model = model


class ProviderError(LLMProviderError):
    """Generic error raised when an LLM provider operation fails."""


class RateLimitError(LLMProviderError):
    """Raised when an LLM provider rate limit is exceeded."""

    error_code: str = RATE_LIMIT_EXCEEDED
    status_code: int = status.HTTP_429_TOO_MANY_REQUESTS


class InvalidModelError(LLMProviderError):
    """Raised when a requested model is invalid, unknown, or unsupported."""

    error_code: str = RESOURCE_NOT_FOUND
    status_code: int = status.HTTP_404_NOT_FOUND


class AuthenticationError(LLMProviderError):
    """Raised when authentication against an LLM provider fails (e.g., API key)."""

    error_code: str = UNAUTHORIZED
    status_code: int = status.HTTP_401_UNAUTHORIZED


class ContextWindowExceededError(LLMProviderError):
    """Raised when the prompt/context size exceeds the model's token limit."""

    error_code: str = VALIDATION_ERROR
    status_code: int = status.HTTP_400_BAD_REQUEST


class ProviderUnavailableError(LLMProviderError):
    """Raised when an LLM provider endpoint is unreachable or down."""

    error_code: str = SERVICE_UNAVAILABLE
    status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE
