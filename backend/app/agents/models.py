"""Agent Core domain models and schemas.

Defines provider-independent request, response, metadata, capability, and status
models for the Agent Core framework.
"""

from __future__ import annotations

import uuid
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from app.infrastructure.llm.conversation import Conversation


class AgentCapability(StrEnum):
    """Capabilities an AI Agent can possess.

    Members:
        PLANNING: Deconstructing problems and building workflow plans.
        RESEARCH: Information retrieval and context analysis.
        ARCHITECTING: Designing structural DAGs and component graphs.
        VALIDATION: Verifying workflow correctness and constraints.
        OPTIMIZATION: Performance tuning and token/cost reduction.
        DOCUMENTATION: Generating markdown guides and documentation.
        SUPERVISION: Orchestrating and managing subagent execution.
        CODE_GENERATION: Code synthesis and script creation.
    """

    PLANNING = "planning"
    RESEARCH = "research"
    ARCHITECTING = "architecting"
    VALIDATION = "validation"
    OPTIMIZATION = "optimization"
    DOCUMENTATION = "documentation"
    SUPERVISION = "supervision"
    CODE_GENERATION = "code_generation"


class AgentStatus(StrEnum):
    """Lifecycle status of an agent execution task.

    Members:
        IDLE: Agent is initialized and ready for execution.
        RUNNING: Agent execution is actively in progress.
        COMPLETED: Agent execution finished successfully.
        FAILED: Agent execution failed with an error.
    """

    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentMetadata(BaseModel):
    """Metadata describing an AI Agent's identity and capabilities.

    Attributes:
        id: Unique stable identifier string for the agent (e.g. 'planner').
        name: Human-readable display name.
        description: Description of the agent's purpose and functionality.
        version: Semantic version of the agent definition.
        capabilities: List of capabilities supported by the agent.
        supported_models: Optional list of preferred/supported model names.
        metadata: Optional key/value metadata map.
    """

    id: str = Field(..., description="Unique agent identifier string.")
    name: str = Field(..., description="Human-readable agent display name.")
    description: str = Field(..., description="Agent description.")
    version: str = Field(default="1.0.0", description="Semantic version string.")
    capabilities: list[AgentCapability] = Field(
        default_factory=list,
        description="Capabilities supported by the agent.",
    )
    supported_models: list[str] = Field(
        default_factory=list,
        description="Supported or preferred model identifiers.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional agent metadata.",
    )


class AgentRequest(BaseModel):
    """Request payload for invoking an AI Agent.

    Attributes:
        agent_id: Target agent identifier.
        user_prompt: User instruction or input prompt string.
        conversation: Optional Conversation instance or message history.
        context: Optional dictionary of domain or environment context.
        model: Optional override model identifier.
        provider: Optional override LLM provider name (e.g. 'openai', 'ollama').
        temperature: Sampling temperature override.
        max_tokens: Maximum tokens override.
    """

    agent_id: str = Field(..., description="Target agent identifier.")
    user_prompt: str = Field(..., description="User prompt or instruction.")
    conversation: Conversation | None = Field(
        default=None,
        description="Active conversation history.",
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Execution context dictionary.",
    )
    model: str | None = Field(
        default=None,
        description="Optional model identifier override.",
    )
    provider: str | None = Field(
        default=None,
        description="Optional provider name override.",
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
        description="Maximum tokens override.",
    )


class AgentResponse(BaseModel):
    """Result payload from an AI Agent execution.

    Attributes:
        agent_id: Identifier of the executing agent.
        execution_id: Unique execution task UUID string.
        status: Final status of the agent execution.
        result: Primary result payload returned by the agent.
        conversation: Updated conversation history.
        metadata: Execution metadata (e.g. model, provider, usage).
        error: Human-readable error message if execution failed.
    """

    agent_id: str = Field(..., description="Executing agent identifier.")
    execution_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Execution task UUID identity.",
    )
    status: AgentStatus = Field(
        default=AgentStatus.COMPLETED,
        description="Execution status.",
    )
    result: Any = Field(
        default=None,
        description="Primary result output of the agent.",
    )
    conversation: Conversation | None = Field(
        default=None,
        description="Updated conversation history.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Execution metadata dictionary.",
    )
    error: str | None = Field(
        default=None,
        description="Error description if status is FAILED.",
    )
