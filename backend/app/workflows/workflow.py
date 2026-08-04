"""Workflow domain model and state transitions.

Encapsulates workflow state, metadata, execution steps, and lifecycle transitions.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from app.workflows.workflow_exceptions import WorkflowStateError
from app.workflows.workflow_models import (
    WorkflowData,
    WorkflowStatus,
    WorkflowStep,
)


class Workflow:
    """Domain model representing a business workflow lifecycle.

    Maintains workflow identity, user request, status transitions, and execution steps.
    """

    def __init__(
        self,
        workflow_name: str,
        user_request: str,
        workflow_id: str | None = None,
        workflow_status: WorkflowStatus = WorkflowStatus.CREATED,
        execution_steps: list[WorkflowStep] | None = None,
        metadata: dict[str, Any] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize Workflow instance.

        Args:
            workflow_name: Name of the workflow.
            user_request: Original user request prompt or goal description.
            workflow_id: Optional unique identifier.
            workflow_status: Initial workflow status.
            execution_steps: Optional pre-configured execution steps.
            metadata: Optional arbitrary workflow metadata.
            created_at: Creation timestamp.
            updated_at: Last update timestamp.
        """
        now = datetime.now(UTC)
        self.workflow_id = workflow_id or str(uuid.uuid4())
        self.workflow_name = workflow_name
        self.user_request = user_request
        self.workflow_status = workflow_status
        self.execution_steps: list[WorkflowStep] = execution_steps or []
        self.metadata: dict[str, Any] = metadata or {}
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    def add_step(self, step: WorkflowStep) -> None:
        """Add an execution step to the workflow.

        Args:
            step: WorkflowStep instance to append.
        """
        self.execution_steps.append(step)
        self._touch()

    def update_status(self, new_status: WorkflowStatus) -> None:
        """Update the workflow lifecycle status.

        Args:
            new_status: Target WorkflowStatus enum member.

        Raises:
            WorkflowStateError: If transition is invalid (e.g. from COMPLETED).
        """
        terminal_states = {WorkflowStatus.COMPLETED, WorkflowStatus.CANCELLED}
        if (
            self.workflow_status in terminal_states
            and new_status not in terminal_states
        ):
            err_msg = f"Cannot transition from terminal state '{self.workflow_status}'"
            raise WorkflowStateError(
                err_msg,
                workflow_id=self.workflow_id,
            )
        self.workflow_status = new_status
        self._touch()

    def mark_ready(self) -> None:
        """Transition workflow status to READY."""
        self.update_status(WorkflowStatus.READY)

    def mark_running(self) -> None:
        """Transition workflow status to RUNNING."""
        self.update_status(WorkflowStatus.RUNNING)

    def mark_paused(self) -> None:
        """Transition workflow status to PAUSED."""
        self.update_status(WorkflowStatus.PAUSED)

    def mark_completed(self) -> None:
        """Transition workflow status to COMPLETED."""
        self.update_status(WorkflowStatus.COMPLETED)

    def mark_failed(self, error: str | None = None) -> None:
        """Transition workflow status to FAILED.

        Args:
            error: Optional error message description.
        """
        if error:
            self.metadata["error"] = error
        self.update_status(WorkflowStatus.FAILED)

    def mark_cancelled(self) -> None:
        """Transition workflow status to CANCELLED."""
        self.update_status(WorkflowStatus.CANCELLED)

    def to_model(self) -> WorkflowData:
        """Serialize domain Workflow into WorkflowData Pydantic schema."""
        return WorkflowData(
            workflow_id=self.workflow_id,
            workflow_name=self.workflow_name,
            user_request=self.user_request,
            workflow_status=self.workflow_status,
            created_at=self.created_at,
            updated_at=self.updated_at,
            execution_steps=self.execution_steps,
            metadata=self.metadata,
        )

    @classmethod
    def from_model(cls, model: WorkflowData) -> Workflow:
        """Instantiate domain Workflow from a WorkflowData schema instance."""
        return cls(
            workflow_id=model.workflow_id,
            workflow_name=model.workflow_name,
            user_request=model.user_request,
            workflow_status=model.workflow_status,
            execution_steps=model.execution_steps,
            metadata=model.metadata,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _touch(self) -> None:
        """Update last modified timestamp."""
        self.updated_at = datetime.now(UTC)
