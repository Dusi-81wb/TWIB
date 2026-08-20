"""Workflow Pydantic schemas for request validation and serialization.

Defines schemas for DAG graph definitions, nodes, edges, validation, execution,
checkpoints, and queries.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class WorkflowNodeSchema(BaseModel):
    """Schema for an individual node within a DAG graph."""

    model_config = {"extra": "allow"}

    node_id: str = Field(..., description="Unique node identifier")
    node_type: str = Field(default="agent", description="Node type: llm, tool, condition, loop, parallel, human, agent, subworkflow")
    name: str = Field(default="", description="Display name")
    description: str = Field(default="", description="Description")
    input_mapping: dict[str, str] = Field(default_factory=dict, description="Input mappings e.g. {'query': '$context.prompt'}")
    optional: bool = Field(default=False, description="Whether failure is non-fatal")
    max_retries: int = Field(default=0, description="Max retries on error")
    retry_delay_seconds: float = Field(default=0.5, description="Backoff base delay")
    timeout_seconds: float | None = Field(default=None, description="Timeout limit in seconds")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Node specific configuration")

    # Node-specific optional properties
    tool_name: str | None = Field(default=None, description="Tool name for ToolNode")
    arguments: dict[str, Any] | None = Field(default=None, description="Static arguments for ToolNode")
    prompt_template: str | None = Field(default=None, description="Prompt template for LLMNode")
    model: str | None = Field(default=None, description="Model identifier")
    provider: str | None = Field(default=None, description="LLM provider")
    agent_id: str | None = Field(default=None, description="Agent ID for AgentNode")
    condition_expression: str | None = Field(default=None, description="Condition expression")
    true_branch_target: str | None = Field(default=None, description="True branch target node")
    false_branch_target: str | None = Field(default=None, description="False branch target node")
    title: str | None = Field(default=None, description="Title for HumanNode")
    instructions: str | None = Field(default=None, description="Instructions for HumanNode")
    assigned_role: str | None = Field(default=None, description="Assigned role for HumanNode")



class WorkflowEdgeSchema(BaseModel):
    """Schema for a directed edge in a DAG graph."""

    source_node_id: str = Field(..., description="Source node ID")
    target_node_id: str = Field(..., description="Target node ID")
    edge_type: str = Field(default="sequence", description="sequence, conditional, parallel, error, compensation")
    condition_expression: str | None = Field(default=None, description="Optional branch condition")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary edge metadata")


class WorkflowGraphSchema(BaseModel):
    """Schema for a complete DAG definition."""

    nodes: list[WorkflowNodeSchema] = Field(default_factory=list, description="Graph nodes")
    edges: list[WorkflowEdgeSchema] = Field(default_factory=list, description="Graph edges")


class CreateWorkflowRequest(BaseModel):
    """Schema for creating a new workflow."""

    workflow_name: str = Field(..., description="Name of the workflow.")
    user_request: str = Field(..., description="Original user prompt or objective.")
    workspace_id: str | None = Field(default=None, description="Optional Workspace ID.")
    graph_definition: WorkflowGraphSchema | dict[str, Any] | None = Field(
        default=None,
        description="Optional DAG graph definition with nodes and edges.",
    )
    steps: list[dict[str, Any]] | None = Field(
        default=None,
        description="Optional list of step definitions (legacy pipeline format).",
    )
    metadata: dict[str, Any] | None = Field(
        default=None,
        description="Optional arbitrary metadata.",
    )


class ValidateGraphRequest(BaseModel):
    """Schema for validating a workflow DAG structure."""

    graph: WorkflowGraphSchema | dict[str, Any] = Field(..., description="DAG graph definition to validate")


class ValidateGraphResponse(BaseModel):
    """Schema for graph validation results."""

    is_valid: bool
    cycles_detected: list[list[str]] = Field(default_factory=list)
    execution_waves: list[list[str]] = Field(default_factory=list)
    topological_order: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class ExecuteWorkflowRequest(BaseModel):
    """Schema for triggering execution of a workflow."""

    context: dict[str, Any] | None = Field(default=None, description="Execution parameters or variable overrides")


class ReviewCheckpointRequest(BaseModel):
    """Schema for reviewing a human checkpoint."""

    action: str = Field(..., description="approve, reject, or request_changes")
    comments: str | None = Field(default=None, description="Review feedback or instructions")


class ResumeWorkflowRequest(BaseModel):
    """Schema for resuming a paused/checkpointed workflow."""

    checkpoint_id: str | None = Field(default=None, description="Optional checkpoint ID")
    context_override: dict[str, Any] | None = Field(default=None, description="Additional context parameters")


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
    graph_definition: dict[str, Any] = Field(default_factory=dict)
    execution_steps: list[WorkflowStepResponse] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowExecutionResponse(BaseModel):
    """Schema representing a workflow execution instance."""

    execution_id: str
    workflow_id: str
    status: str
    context: dict[str, Any] = Field(default_factory=dict)
    node_states: dict[str, Any] = Field(default_factory=dict)
    step_outputs: dict[str, Any] = Field(default_factory=dict)
    duration_seconds: float = 0.0
    error: str | None = None
    checkpoint_id: str | None = None


class WorkflowCheckpointResponse(BaseModel):
    """Schema representing an approval checkpoint."""

    checkpoint_id: str
    workflow_id: str
    execution_id: str
    step_id: str | None = None
    checkpoint_type: str
    approval_status: str
    title: str
    description: str
    data_to_review: dict[str, Any] = Field(default_factory=dict)
    assigned_role: str | None = None
    requested_by: str | None = None
    reviewed_by: str | None = None
    comments: str | None = None
    created_at: str
    reviewed_at: str | None = None


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
