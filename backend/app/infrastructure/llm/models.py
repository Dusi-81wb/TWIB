"""LLM model metadata abstractions.

Defines provider-independent representation of model metadata and capabilities.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ModelInfo(BaseModel):
    """Provider-independent information about a supported LLM model.

    Attributes:
        id: Unique model identifier (e.g. 'gpt-4o', 'llama3').
        name: Human-readable model display name.
        provider: Provider identifier (e.g. 'openai', 'ollama', 'anthropic').
        context_window: Maximum context window in tokens.
        max_output_tokens: Optional maximum token output limit.
        supports_streaming: Whether the model supports streaming responses.
        supports_tools: Whether the model supports tool/function calling.
        supports_vision: Whether the model supports image/vision inputs.
        metadata: Key/value metadata dictionary.
    """

    id: str = Field(..., description="Unique model identifier.")
    name: str = Field(..., description="Human-readable model name.")
    provider: str = Field(..., description="Owning provider name.")
    context_window: int = Field(
        default=4096,
        ge=1,
        description="Maximum input context window size in tokens.",
    )
    max_output_tokens: int | None = Field(
        default=None,
        ge=1,
        description="Maximum allowed completion token output limit.",
    )
    supports_streaming: bool = Field(
        default=True,
        description="Whether streaming completions are supported.",
    )
    supports_tools: bool = Field(
        default=False,
        description="Whether function/tool calling is supported.",
    )
    supports_vision: bool = Field(
        default=False,
        description="Whether multimodal vision inputs are supported.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Model metadata dictionary.",
    )
