"""Domain value objects for the Workflow Subsystem.

Defines immutable value objects and enums representing workflow statuses, node statuses,
edge types, checkpoint types, approval statuses, edges, and node execution state snapshots.
Strictly decoupled from infrastructure frameworks (FastAPI, SQLAlchemy, Redis, etc.).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class WorkflowStatus(StrEnum):
    """Lifecycle status of a business workflow."""

    CREATED = "created"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NodeStatus(StrEnum):
    """Execution status of an individual node in a workflow graph."""

    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    RETRYING = "retrying"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    PAUSED = "paused"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    CANCELLED = "cancelled"


class EdgeType(StrEnum):
    """Routing relationship type between nodes in a workflow graph."""

    SEQUENCE = "sequence"
    CONDITIONAL = "conditional"
    PARALLEL = "parallel"
    ERROR = "error"
    COMPENSATION = "compensation"


class CheckpointType(StrEnum):
    """Classification for workflow execution checkpoints."""

    STATE_SNAPSHOT = "state_snapshot"
    HUMAN_APPROVAL = "human_approval"
    ARCHITECTURE_APPROVAL = "architecture_approval"
    RESEARCH_APPROVAL = "research_approval"
    DOCUMENTATION_APPROVAL = "documentation_approval"
    FINAL_APPROVAL = "final_approval"


class ApprovalStatus(StrEnum):
    """Status of a human review checkpoint."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"


@dataclass(frozen=True)
class WorkflowEdge:
    """Immutable value object representing a directed edge in a Workflow DAG."""

    source_node_id: str
    target_node_id: str
    edge_type: EdgeType = EdgeType.SEQUENCE
    condition_expression: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize edge to dictionary."""
        return {
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "edge_type": str(self.edge_type.value if hasattr(self.edge_type, "value") else self.edge_type),
            "condition_expression": self.condition_expression,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorkflowEdge:
        """Deserialize edge from dictionary."""
        edge_type_raw = data.get("edge_type", EdgeType.SEQUENCE)
        try:
            edge_type = EdgeType(edge_type_raw)
        except ValueError:
            edge_type = EdgeType.SEQUENCE

        return cls(
            source_node_id=data["source_node_id"],
            target_node_id=data["target_node_id"],
            edge_type=edge_type,
            condition_expression=data.get("condition_expression"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class NodeExecutionState:
    """Mutable domain model tracking the execution snapshot of a specific node."""

    node_id: str
    status: NodeStatus = NodeStatus.PENDING
    attempt: int = 0
    max_retries: int = 0
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_seconds: float = 0.0
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def mark_running(self) -> None:
        """Transition node state to running."""
        self.status = NodeStatus.RUNNING
        self.started_at = datetime.now(UTC)
        self.attempt += 1

    def mark_retrying(self, error: str) -> None:
        """Transition node state to retrying."""
        self.status = NodeStatus.RETRYING
        self.error = error

    def mark_completed(self, outputs: dict[str, Any]) -> None:
        """Transition node state to completed."""
        self.status = NodeStatus.COMPLETED
        self.completed_at = datetime.now(UTC)
        self.outputs = outputs
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()

    def mark_failed(self, error: str) -> None:
        """Transition node state to failed."""
        self.status = NodeStatus.FAILED
        self.completed_at = datetime.now(UTC)
        self.error = error
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()

    def mark_skipped(self, reason: str = "Dependency not satisfied or branch inactive") -> None:
        """Transition node state to skipped."""
        self.status = NodeStatus.SKIPPED
        self.error = reason

    def mark_waiting_approval(self) -> None:
        """Transition node state to waiting for approval."""
        self.status = NodeStatus.WAITING_FOR_APPROVAL

    def to_dict(self) -> dict[str, Any]:
        """Serialize state snapshot to dictionary."""
        return {
            "node_id": self.node_id,
            "status": str(self.status.value if hasattr(self.status, "value") else self.status),
            "attempt": self.attempt,
            "max_retries": self.max_retries,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NodeExecutionState:
        """Deserialize state snapshot from dictionary."""
        status_raw = data.get("status", NodeStatus.PENDING)
        try:
            status = NodeStatus(status_raw)
        except ValueError:
            status = NodeStatus.PENDING

        started_at = (
            datetime.fromisoformat(data["started_at"])
            if data.get("started_at")
            else None
        )
        completed_at = (
            datetime.fromisoformat(data["completed_at"])
            if data.get("completed_at")
            else None
        )

        return cls(
            node_id=data["node_id"],
            status=status,
            attempt=data.get("attempt", 0),
            max_retries=data.get("max_retries", 0),
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=data.get("duration_seconds", 0.0),
            inputs=data.get("inputs", {}),
            outputs=data.get("outputs", {}),
            error=data.get("error"),
        )
