"""Domain events for the Workflow Subsystem.

Defines decoupled domain event models emitted throughout the lifecycle of workflows,
nodes, executions, and human review checkpoints.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
import uuid

from app.domain.event import DomainEvent


@dataclass(frozen=True)
class WorkflowCreatedEvent(DomainEvent):
    """Emitted when a new workflow aggregate is registered."""

    workflow_id: str
    workflow_name: str
    workspace_id: str | None = None
    node_count: int = 0
    edge_count: int = 0


@dataclass(frozen=True)
class WorkflowStartedEvent(DomainEvent):
    """Emitted when a workflow execution begins."""

    workflow_id: str
    execution_id: str
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class WorkflowCompletedEvent(DomainEvent):
    """Emitted when a workflow execution finishes successfully."""

    workflow_id: str
    execution_id: str
    duration_seconds: float = 0.0
    outputs: dict[str, Any] = field(default_factory=dict)
    completed_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class WorkflowFailedEvent(DomainEvent):
    """Emitted when a workflow execution fails catastrophically."""

    workflow_id: str
    execution_id: str
    error: str = ""
    failed_node_id: str | None = None
    failed_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class WorkflowCancelledEvent(DomainEvent):
    """Emitted when an execution is explicitly cancelled."""

    workflow_id: str
    execution_id: str
    cancelled_by: str | None = None
    cancelled_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class WorkflowPausedEvent(DomainEvent):
    """Emitted when a workflow is paused for human review or approval."""

    workflow_id: str
    execution_id: str
    checkpoint_id: str
    reason: str = "Awaiting human review"


@dataclass(frozen=True)
class WorkflowResumedEvent(DomainEvent):
    """Emitted when a paused/checkpointed workflow resumes execution."""

    workflow_id: str
    execution_id: str
    checkpoint_id: str | None = None
    resumed_by: str | None = None


@dataclass(frozen=True)
class NodeStartedEvent(DomainEvent):
    """Emitted when a specific node starts execution."""

    workflow_id: str
    execution_id: str
    node_id: str
    node_type: str
    attempt: int = 1


@dataclass(frozen=True)
class NodeRetryingEvent(DomainEvent):
    """Emitted when a node encounters a transient error and initiates a retry."""

    workflow_id: str
    execution_id: str
    node_id: str
    attempt: int
    max_retries: int
    delay_seconds: float
    error: str


@dataclass(frozen=True)
class NodeCompletedEvent(DomainEvent):
    """Emitted when a specific node execution finishes successfully."""

    workflow_id: str
    execution_id: str
    node_id: str
    node_type: str
    duration_seconds: float
    outputs: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class NodeFailedEvent(DomainEvent):
    """Emitted when a node fails execution."""

    workflow_id: str
    execution_id: str
    node_id: str
    node_type: str
    error: str
    optional: bool = False


@dataclass(frozen=True)
class NodeSkippedEvent(DomainEvent):
    """Emitted when a node is skipped due to inactive branch or missing prerequisite."""

    workflow_id: str
    execution_id: str
    node_id: str
    reason: str = ""


@dataclass(frozen=True)
class CheckpointCreatedEvent(DomainEvent):
    """Emitted when a human approval checkpoint is instantiated."""

    checkpoint_id: str
    workflow_id: str
    execution_id: str
    step_id: str | None
    checkpoint_type: str
    title: str


@dataclass(frozen=True)
class CheckpointApprovedEvent(DomainEvent):
    """Emitted when a reviewer approves a checkpoint."""

    checkpoint_id: str
    workflow_id: str
    execution_id: str
    reviewed_by: str
    comments: str | None = None


@dataclass(frozen=True)
class CheckpointRejectedEvent(DomainEvent):
    """Emitted when a reviewer rejects a checkpoint."""

    checkpoint_id: str
    workflow_id: str
    execution_id: str
    reviewed_by: str
    comments: str | None = None
