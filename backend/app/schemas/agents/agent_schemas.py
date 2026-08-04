"""Agent execution Pydantic schemas for request validation.

Defines transport schemas for agent execution endpoints.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AgentExecuteRequest(BaseModel):
    """Transport schema for executing an AI Agent."""

    user_prompt: str = Field(..., description="User prompt or task objective.")
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional environment or domain context dictionary.",
    )
    model: str | None = Field(
        default=None,
        description="Optional LLM model override.",
    )
    provider: str | None = Field(
        default=None,
        description="Optional LLM provider override ('openai', 'ollama').",
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature.",
    )
    max_tokens: int | None = Field(
        default=None,
        ge=1,
        description="Maximum tokens limit.",
    )
