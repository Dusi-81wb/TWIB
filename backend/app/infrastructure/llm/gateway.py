"""Abstract LLM Gateway interface.

Defines a provider-agnostic interface for chat completions, prompt completions,
and health checks across gateway implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from app.infrastructure.llm.message import ChatMessage
from app.infrastructure.llm.models import GatewayResponse


class LLMGateway(ABC):
    """Abstract interface for provider-agnostic LLM Gateways."""

    @abstractmethod
    async def chat(
        self,
        messages: Sequence[ChatMessage | dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float | None = None,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> GatewayResponse:
        """Send a sequence of messages for chat completion.

        Args:
            messages: Conversation messages (as ChatMessage objects or dicts).
            model: Optional override model identifier.
            temperature: Optional sampling temperature override.
            system_prompt: Optional prepended system message.
            **kwargs: Additional parameters passed to the gateway endpoint.

        Returns:
            TWIB-specific GatewayResponse object.
        """

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        *,
        model: str | None = None,
        temperature: float | None = None,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> GatewayResponse:
        """Send a single prompt string for completion.

        Args:
            prompt: Text prompt input string.
            model: Optional override model identifier.
            temperature: Optional sampling temperature override.
            system_prompt: Optional system instructions.
            **kwargs: Additional parameters passed to the gateway endpoint.

        Returns:
            TWIB-specific GatewayResponse object.
        """

    @abstractmethod
    async def health(self) -> dict[str, Any]:
        """Check the operational health and connectivity of the gateway.

        Returns:
            Dictionary containing health status, latency, and provider metadata.
        """
