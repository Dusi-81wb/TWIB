"""Agent execution Pydantic schemas for request validation.

Defines transport schemas for agent execution and conversations.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AgentInfoResponse(BaseModel):
    """Transport schema for describing registered agent capabilities."""

    id: str = Field(..., description="Agent identifier string.")
    name: str = Field(..., description="Display name of agent.")
    type: str = Field(..., description="Type key of agent.")
    role: str = Field(..., description="Primary role declaration.")
    description: str = Field(..., description="Detailed description.")
    capabilities: list[str] = Field(
        default_factory=list,
        description="Capabilities list.",
    )


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


class ResearchRunRequest(BaseModel):
    """Transport schema for running ResearchAgent synchronously via LLMGateway."""

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Research prompt or query topic.",
        examples=["Explain distributed consensus algorithms"],
    )
    temperature: float = Field(
        default=0.3,
        ge=0.0,
        le=2.0,
        description="Sampling temperature for LLM completion.",
        examples=[0.3],
    )
    model: str | None = Field(
        default=None,
        max_length=255,
        description="Target model identifier (optional, auto-routes to configured/loaded model if omitted).",
    )


class ResearchExecutionItemResponse(BaseModel):
    """Transport schema for a stored ResearchAgent execution record."""

    id: uuid.UUID = Field(..., description="Execution record UUID.")
    user_id: uuid.UUID = Field(..., description="Owner user UUID.")
    prompt: str = Field(..., description="User research query prompt.")
    response: str = Field(..., description="LLM Gateway answer text.")
    provider: str = Field(..., description="LLM provider name.")
    model: str = Field(..., description="LLM model identifier.")
    latency_ms: float = Field(..., description="Execution duration in milliseconds.")
    usage: dict[str, Any] = Field(
        default_factory=dict,
        description="Token usage metrics.",
    )
    created_at: datetime = Field(..., description="Execution timestamp.")


class CreateConversationRequest(BaseModel):
    """Transport schema for creating a new research conversation."""

    title: str | None = Field(
        default=None,
        max_length=255,
        description="Optional initial conversation title.",
    )
    agent_type: str = Field(
        default="research",
        description="Agent identifier ('research').",
    )


class SendMessageRequest(BaseModel):
    """Transport schema for sending a user message turn within a conversation."""

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User text prompt or message content.",
    )
    temperature: float = Field(
        default=0.3,
        ge=0.0,
        le=2.0,
        description="Sampling temperature for completion.",
    )
    model: str | None = Field(
        default=None,
        max_length=255,
        description="Target model identifier (optional, auto-routes to configured/loaded model if omitted).",
    )


class ResearchMessageResponse(BaseModel):
    """Transport schema for a single message turn in a conversation."""

    id: uuid.UUID = Field(..., description="Message UUID.")
    conversation_id: uuid.UUID = Field(..., description="Parent conversation UUID.")
    role: str = Field(..., description="Role ('user', 'assistant', 'system').")
    content: str = Field(..., description="Text content of message turn.")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Turn metadata (provider, model, latency_ms, usage).",
    )
    created_at: datetime = Field(..., description="Message creation timestamp.")


class ResearchConversationResponse(BaseModel):
    """Transport schema for conversation item summary."""

    id: uuid.UUID = Field(..., description="Conversation UUID.")
    user_id: uuid.UUID = Field(..., description="Owner user UUID.")
    title: str = Field(..., description="Title of the conversation thread.")
    agent_type: str = Field(..., description="Agent type identifier ('research').")
    created_at: datetime = Field(..., description="Creation timestamp.")
    updated_at: datetime = Field(..., description="Last update timestamp.")
    last_message_snippet: str | None = Field(
        default=None,
        description="Snippet of the latest message turn.",
    )


class ResearchConversationDetailResponse(BaseModel):
    """Transport schema for full conversation details including message turns."""

    id: uuid.UUID = Field(..., description="Conversation UUID.")
    user_id: uuid.UUID = Field(..., description="Owner user UUID.")
    title: str = Field(..., description="Title of conversation thread.")
    agent_type: str = Field(..., description="Agent type identifier ('research').")
    created_at: datetime = Field(..., description="Creation timestamp.")
    updated_at: datetime = Field(..., description="Last update timestamp.")
    messages: list[ResearchMessageResponse] = Field(
        default_factory=list,
        description="Ordered list of message turns.",
    )
