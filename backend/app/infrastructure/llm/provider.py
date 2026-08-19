"""Abstract LLM Provider interface.

Defines the contract that every LLM provider implementation (OpenAI, Ollama,
Anthropic, etc.) must implement. This abstraction decouples business logic, AI
agents, and model routers from provider-specific APIs and SDKs.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any

from app.infrastructure.llm.models import ModelInfo
from app.infrastructure.llm.response import ChatRequest, ChatResponse, StreamChunk


class LLMProvider(ABC):
    """Abstract interface for LLM providers.

    Every concrete provider implementation must subclass this class and
    provide async implementations for completion, streaming, model listing,
    and health check operations.

    Attributes:
        provider_name: Stable identifier of the provider (e.g. 'openai').
    """

    provider_name: str = "abstract"

    def __init__(self, settings: Any = None, **kwargs: Any) -> None:
        """Initialize provider instance."""
        _ = (settings, kwargs)

    @abstractmethod
    async def complete(self, request: ChatRequest) -> ChatResponse:
        """Execute a non-streaming chat completion request.

        Args:
            request: Provider-independent ChatRequest payload.

        Returns:
            Provider-independent ChatResponse object.

        Raises:
            LLMProviderError: If the completion fails.
        """
        ...

    @abstractmethod
    def stream(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        """Execute a streaming chat completion request.

        Args:
            request: Provider-independent ChatRequest payload.

        Yields:
            Provider-independent StreamChunk objects as they arrive.

        Raises:
            LLMProviderError: If the stream fails.
        """
        ...

    @abstractmethod
    async def list_models(self) -> list[ModelInfo]:
        """List all models supported by this provider.

        Returns:
            Sequence of ModelInfo metadata objects.

        Raises:
            LLMProviderError: If listing models fails.
        """
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check whether the LLM provider endpoint is healthy and accessible.

        Returns:
            True if healthy and reachable, False otherwise.
        """
        ...
