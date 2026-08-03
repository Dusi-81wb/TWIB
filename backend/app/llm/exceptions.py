"""LLM exceptions alias module."""

from app.infrastructure.llm.exceptions import (
    AuthenticationError,
    ContextWindowExceededError,
    InvalidModelError,
    LLMProviderError,
    ProviderError,
    ProviderUnavailableError,
    RateLimitError,
)

__all__ = [
    "AuthenticationError",
    "ContextWindowExceededError",
    "InvalidModelError",
    "LLMProviderError",
    "ProviderError",
    "ProviderUnavailableError",
    "RateLimitError",
]
