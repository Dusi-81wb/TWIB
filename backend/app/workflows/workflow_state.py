"""Workflow state models and transition rules.

Defines StateHistoryEntry, WorkflowState structures, and transition validation.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from app.workflows.workflow_exceptions import WorkflowStateError
from app.workflows.workflow_models import WorkflowStatus

ALLOWED_TRANSITIONS: dict[WorkflowStatus, set[WorkflowStatus]] = {
    WorkflowStatus.CREATED: {
        WorkflowStatus.READY,
        WorkflowStatus.RUNNING,
        WorkflowStatus.WAITING_FOR_APPROVAL,
        WorkflowStatus.CANCELLED,
        WorkflowStatus.FAILED,
    },
    WorkflowStatus.READY: {
        WorkflowStatus.RUNNING,
        WorkflowStatus.WAITING_FOR_APPROVAL,
        WorkflowStatus.CANCELLED,
        WorkflowStatus.FAILED,
    },
    WorkflowStatus.RUNNING: {
        WorkflowStatus.PAUSED,
        WorkflowStatus.WAITING_FOR_APPROVAL,
        WorkflowStatus.COMPLETED,
        WorkflowStatus.FAILED,
        WorkflowStatus.CANCELLED,
    },
    WorkflowStatus.PAUSED: {
        WorkflowStatus.RUNNING,
        WorkflowStatus.CANCELLED,
        WorkflowStatus.FAILED,
    },
    WorkflowStatus.WAITING_FOR_APPROVAL: {
        WorkflowStatus.RUNNING,
        WorkflowStatus.CANCELLED,
        WorkflowStatus.FAILED,
    },
    WorkflowStatus.COMPLETED: set(),
    WorkflowStatus.FAILED: set(),
    WorkflowStatus.CANCELLED: set(),
}


class StateHistoryEntry(BaseModel):
    """Immutable audit record of a single workflow state transition."""

    previous_state: WorkflowStatus | None = Field(
        default=None,
        description="Previous status prior to transition.",
    )
    current_state: WorkflowStatus = Field(
        ...,
        description="New status after transition.",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp of the state transition event.",
    )
    triggering_event: str = Field(
        default="user_action",
        description="Triggering event name or identifier.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context metadata associated with transition.",
    )


class WorkflowState(BaseModel):
    """Persisted snapshot of a workflow execution state and transition history."""

    workflow_id: str = Field(..., description="Unique workflow identifier.")
    current_state: WorkflowStatus = Field(
        default=WorkflowStatus.CREATED,
        description="Current lifecycle status.",
    )
    history: list[StateHistoryEntry] = Field(
        default_factory=list,
        description="Chronological audit history of state transitions.",
    )
    state_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary persisted state variables and step outputs.",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Last state modification timestamp.",
    )


def validate_state_transition(
    workflow_id: str,
    from_state: WorkflowStatus,
    to_state: WorkflowStatus,
) -> bool:
    """Validate whether a state transition from `from_state` to `to_state` is permitted.

    Args:
        workflow_id: Workflow instance identifier.
        from_state: Starting status.
        to_state: Target status.

    Returns:
        True if transition is allowed.

    Raises:
        WorkflowStateError: If transition is invalid.
    """
    if from_state == to_state:
        return True

    allowed = ALLOWED_TRANSITIONS.get(from_state, set())
    if to_state not in allowed:
        err_msg = f"Invalid state transition: '{from_state}' -> '{to_state}'"
        raise WorkflowStateError(
            err_msg,
            workflow_id=workflow_id,
        )
    return True
