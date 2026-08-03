"""LLM Streaming abstraction.

Provides an async stream wrapper for consuming, accumulating, and cancelling
LLM provider stream output in a unified format.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any

from app.infrastructure.llm.message import ChatMessage, MessageRole
from app.infrastructure.llm.response import (
    ChatResponse,
    CompletionUsage,
    StreamChunk,
)


class AsyncStreamWrapper:
    """Async wrapper around an LLM provider's StreamChunk iterator.

    Provides cancellation control, text accumulation, and SSE formatting.

    Attributes:
        _stream: Underlying AsyncIterator yielding StreamChunk instances.
        _cancelled: Flag indicating whether stream consumption was cancelled.
        _accumulated_text: Text accumulated from stream chunks so far.
        _final_usage: Consolidated completion usage accumulated from stream.
    """

    def __init__(self, stream: AsyncIterator[StreamChunk]) -> None:
        """Initialize AsyncStreamWrapper.

        Args:
            stream: Underlying StreamChunk async iterator.
        """
        self._stream = stream
        self._cancelled = False
        self._accumulated_text = ""
        self._final_usage: CompletionUsage | None = None

    @property
    def is_cancelled(self) -> bool:
        """Return whether stream consumption was cancelled.

        Returns:
            True if cancelled, False otherwise.
        """
        return self._cancelled

    def cancel(self) -> None:
        """Cancel further stream consumption."""
        self._cancelled = True

    async def __aiter__(self) -> AsyncIterator[StreamChunk]:
        """Iterate over incoming stream chunks until finished or cancelled.

        Yields:
            StreamChunk objects from the provider.
        """
        async for chunk in self._stream:
            if self._cancelled:
                break
            if chunk.delta:
                self._accumulated_text += chunk.delta
            if chunk.usage:
                self._final_usage = chunk.usage
            yield chunk

    async def accumulate_text(self) -> str:
        """Consume the entire stream and return accumulated completion text.

        Returns:
            Full generated completion string.
        """
        async for _ in self:
            pass
        return self._accumulated_text

    async def accumulate_response(
        self,
        model: str = "unknown",
        provider: str = "unknown",
    ) -> ChatResponse:
        """Consume the stream and return a consolidated ChatResponse object.

        Args:
            model: Model name fallback if chunks omit it.
            provider: Provider name fallback if chunks omit it.

        Returns:
            Consolidated ChatResponse instance.
        """
        last_chunk: StreamChunk | None = None
        async for chunk in self:
            last_chunk = chunk

        response_id = last_chunk.id if last_chunk else "unknown"
        response_model = last_chunk.model if last_chunk else model
        response_provider = last_chunk.provider if last_chunk else provider
        finish_reason = (
            last_chunk.finish_reason
            if last_chunk and last_chunk.finish_reason
            else "stop"
        )

        return ChatResponse(
            id=response_id,
            model=response_model,
            provider=response_provider,
            message=ChatMessage(
                role=MessageRole.ASSISTANT,
                content=self._accumulated_text,
            ),
            finish_reason=finish_reason,
            usage=self._final_usage or CompletionUsage(),
        )

    async def to_sse(self) -> AsyncIterator[str]:
        """Format stream chunks into Server-Sent Events (SSE) data lines.

        Yields:
            SSE-formatted event string chunks (`data: {...}\n\n`).
        """
        async for chunk in self:
            payload: dict[str, Any] = {
                "id": chunk.id,
                "model": chunk.model,
                "provider": chunk.provider,
                "delta": chunk.delta,
            }
            if chunk.finish_reason:
                payload["finish_reason"] = chunk.finish_reason
            if chunk.usage:
                payload["usage"] = chunk.usage.model_dump()
            yield f"data: {json.dumps(payload)}\n\n"
        yield "data: [DONE]\n\n"
