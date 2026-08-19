"""Workflow Pydantic schemas for request validation and serialization.

Defines schemas for workflow CRUD, template instantiation, and queries.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CreateWorkflowRequest(BaseModel):
    """Schema for creating a new workflow."""

    workflow_name: str = Field(..., description="Name of the workflow.")
    user_request: str = Field(..., description="Original user prompt or objective.")
    steps: list[dict[str, Any]] | None = Field(
        default=None,
        description="Optional list of step definitions.",
    )
    metadata: dict[str, Any] | None = Field(
        default=None,
        description="Optional arbitrary metadata.",
    )


class InstantiateTemplateRequest(BaseModel):
    """Schema for instantiating a workflow from a template."""

    user_request: str = Field(..., description="User prompt or goal description.")
    custom_name: str | None = Field(
        default=None,
        description="Optional custom workflow name override.",
    )
    configuration_overrides: dict[str, Any] | None = Field(
        default=None,
        description="Optional configuration overrides.",
    )


class WorkflowStepResponse(BaseModel):
    """Schema representing an execution step response."""

    step_id: str
    name: str
    agent_id: str | None = None
    status: str
    input_data: dict[str, Any] = Field(default_factory=dict)
    output_data: dict[str, Any] | None = None
    error: str | None = None
    started_at: str | None = None
    completed_at: str | None = None


class WorkflowResponse(BaseModel):
    """Schema representing detailed workflow information response."""

    workflow_id: str
    workflow_name: str
    user_request: str
    workflow_status: str
    created_at: str
    updated_at: str
    execution_steps: list[WorkflowStepResponse] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowListResponse(BaseModel):
    """Schema for paginated/listed workflow responses."""

    items: list[WorkflowResponse]
    total: int


class WorkflowTemplateResponse(BaseModel):
    """Schema representing workflow template details response."""

    template_id: str
    template_name: str
    description: str
    category: str
    workflow_definition: dict[str, Any] = Field(default_factory=dict)
    default_configuration: dict[str, Any] = Field(default_factory=dict)
    supported_agents: list[str] = Field(default_factory=list)
    requires_approval: bool
    version: str


class WorkflowTemplateListResponse(BaseModel):
    """Schema for listed workflow template responses."""

    items: list[WorkflowTemplateResponse]
    total: int


class StateHistoryEntryResponse(BaseModel):
    """Schema for state history audit record entry."""

    previous_state: str | None = None
    current_state: str
    timestamp: str
    triggering_event: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class StateHistoryResponse(BaseModel):
    """Schema for state history query response."""

    workflow_id: str
    history: list[StateHistoryEntryResponse]
