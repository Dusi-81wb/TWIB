"""LLM model metadata and Gateway response abstractions.

Defines provider-independent representations of model metadata, gateway responses,
and token usage.
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


class GatewayUsage(BaseModel):
    """Token usage metrics for a gateway completion request.

    Attributes:
        prompt_tokens: Number of tokens in the prompt.
        completion_tokens: Number of tokens generated in completion.
        total_tokens: Total tokens consumed.
    """

    prompt_tokens: int = Field(default=0, ge=0, description="Tokens in prompt.")
    completion_tokens: int = Field(
        default=0, ge=0, description="Tokens in completion."
    )
    total_tokens: int = Field(default=0, ge=0, description="Total tokens used.")


class GatewayResponse(BaseModel):
    """TWIB-specific response model returned by LLM Gateways.

    Attributes:
        answer: Generated text answer or completion output.
        provider: Name of the gateway provider (e.g., 'omniroute').
        model: Target model identifier used for generation.
        latency_ms: Request duration in milliseconds.
        usage: Token usage breakdown.
    """

    answer: str = Field(..., description="The generated completion text answer.")
    provider: str = Field(
        default="omniroute", description="The gateway provider identifier."
    )
    model: str = Field(..., description="Target model identifier used.")
    latency_ms: float = Field(
        default=0.0, ge=0.0, description="Response latency in milliseconds."
    )
    usage: GatewayUsage = Field(
        default_factory=GatewayUsage, description="Token usage details."
    )
