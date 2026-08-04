"""Workflow models and schemas.

Defines Pydantic models, status enums, and data structures for the Workflow Engine core.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class WorkflowStatus(StrEnum):
    """Lifecycle status of a business workflow execution.

    Members:
        CREATED: Workflow is instantiated but not yet validated/ready.
        READY: Workflow is validated and ready for execution.
        RUNNING: Workflow execution is actively in progress.
        PAUSED: Workflow execution is temporarily paused.
        COMPLETED: Workflow execution finished successfully.
        FAILED: Workflow execution failed with an unrecoverable error.
        CANCELLED: Workflow execution was explicitly cancelled.
    """

    CREATED = "created"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStep(BaseModel):
    """Individual execution step within a workflow DAG or pipeline."""

    step_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique step identifier.",
    )
    name: str = Field(..., description="Human-readable step name.")
    agent_id: str | None = Field(
        default=None,
        description="ID of the AI agent assigned to execute this step.",
    )
    status: WorkflowStatus = Field(
        default=WorkflowStatus.CREATED,
        description="Current execution status of this step.",
    )
    input_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Input context parameters for the step.",
    )
    output_data: dict[str, Any] | None = Field(
        default=None,
        description="Execution output data returned by the step.",
    )
    error: str | None = Field(
        default=None,
        description="Error description if step execution failed.",
    )
    started_at: datetime | None = Field(
        default=None,
        description="Timestamp when step execution started.",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="Timestamp when step execution completed.",
    )


class WorkflowData(BaseModel):
    """Base dataset schema representing a business workflow state."""

    workflow_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique workflow instance identifier.",
    )
    workflow_name: str = Field(..., description="Name of the workflow.")
    user_request: str = Field(..., description="Original user prompt or goal.")
    workflow_status: WorkflowStatus = Field(
        default=WorkflowStatus.CREATED,
        description="Current lifecycle status of the workflow.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Creation timestamp.",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Last modification timestamp.",
    )
    execution_steps: list[WorkflowStep] = Field(
        default_factory=list,
        description="List of execution steps in the workflow.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary execution metadata.",
    )
