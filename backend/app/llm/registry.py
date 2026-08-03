"""LLM registry alias module."""

from app.infrastructure.llm.registry import (
    LLMProviderRegistry,
    default_registry,
    get_default_registry,
)

__all__ = [
    "LLMProviderRegistry",
    "default_registry",
    "get_default_registry",
]
