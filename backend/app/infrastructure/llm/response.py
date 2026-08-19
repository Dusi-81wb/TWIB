"""LLM request and response models.

Defines provider-independent completion request, response, token usage, and
streaming chunk abstractions.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from app.infrastructure.llm.message import ChatMessage


class CompletionUsage(BaseModel):
    """Token consumption accounting for a completion request.

    Attributes:
        prompt_tokens: Number of input/prompt tokens consumed.
        completion_tokens: Number of output/completion tokens generated.
        total_tokens: Total tokens consumed (prompt + completion).
    """

    prompt_tokens: int = Field(default=0, ge=0, description="Input tokens used.")
    completion_tokens: int = Field(default=0, ge=0, description="Output tokens used.")
    total_tokens: int = Field(default=0, ge=0, description="Total tokens used.")


class ChatRequest(BaseModel):
    """Provider-independent request for LLM chat completion.

    Attributes:
        model: Target model identifier string.
        messages: Ordered sequence of chat messages.
        temperature: Sampling temperature (0.0 to 2.0).
        top_p: Nucleus sampling probability parameter.
        max_tokens: Maximum completion tokens to generate.
        stream: Whether output should be streamed as chunks.
        stop: Optional list of stop sequences.
        metadata: Optional request metadata.
    """

    model: str = Field(..., description="Target model identifier (e.g. 'gpt-4o').")
    messages: list[ChatMessage] = Field(
        ...,
        min_length=1,
        description="List of conversation messages.",
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature.",
    )
    top_p: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling probability.",
    )
    max_tokens: int | None = Field(
        default=None,
        ge=1,
        description="Maximum tokens to generate.",
    )
    stream: bool = Field(
        default=False,
        description="Whether to stream the completion output.",
    )
    stop: list[str] | None = Field(
        default=None,
        description="Optional list of stop sequences.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Request metadata dictionary.",
    )


class ChatResponse(BaseModel):
    """Provider-independent response from an LLM chat completion.

    Attributes:
        id: Unique response or completion ID.
        model: Target model used for completion.
        provider: Provider identifier (e.g. 'openai', 'ollama').
        message: Generated assistant ChatMessage.
        finish_reason: Reason generation stopped (e.g. 'stop', 'length').
        usage: Token usage summary.
        created_at: UTC timestamp when response was completed.
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique completion response ID.",
    )
    model: str = Field(..., description="Model identifier used.")
    provider: str = Field(..., description="Provider identifier.")
    message: ChatMessage = Field(..., description="Generated assistant message.")
    finish_reason: str = Field(
        default="stop",
        description="Termination reason (e.g. 'stop', 'length', 'tool_calls').",
    )
    usage: CompletionUsage = Field(
        default_factory=CompletionUsage,
        description="Token consumption summary.",
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="ISO 8601 UTC timestamp of creation.",
    )


class StreamChunk(BaseModel):
    """Provider-independent streaming delta chunk for LLM output.

    Attributes:
        id: Response or completion chunk ID.
        model: Target model identifier.
        provider: Provider identifier.
        delta: Incremental text snippet generated in this chunk.
        finish_reason: Optional termination reason on final chunk.
        usage: Optional final token usage summary.
    """

    id: str = Field(..., description="Chunk or completion ID.")
    model: str = Field(..., description="Model identifier.")
    provider: str = Field(..., description="Provider identifier.")
    delta: str = Field(..., description="Incremental content snippet.")
    finish_reason: str | None = Field(
        default=None,
        description="Termination reason when generation completes.",
    )
    usage: CompletionUsage | None = Field(
        default=None,
        description="Optional final token usage summary.",
    )
