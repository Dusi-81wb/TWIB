"""Workflow State Manager implementation.

Provides state management, validation of state transitions, historical audit tracking,
and state restoration for workflow executions.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.domain.repositories.unit_of_work import UnitOfWork
from app.workflows.workflow_exceptions import (
    WorkflowNotFoundError,
    WorkflowStateError,
    WorkflowValidationError,
)
from app.workflows.workflow_models import WorkflowStatus
from app.workflows.workflow_state import (
    StateHistoryEntry,
    WorkflowState,
    validate_state_transition,
)


class WorkflowStateManager:
    """Workflow State Manager.

    Handles persistence, transition validation, state history tracking, and rollback
    restoration of workflow execution state.
    """

    def __init__(
        self,
        uow: UnitOfWork | None = None,
    ) -> None:
        """Initialize WorkflowStateManager.

        Args:
            uow: Optional UnitOfWork instance for transaction persistence.
        """
        self._uow = uow
        self._states: dict[str, WorkflowState] = {}

    def save_state(self, workflow_id: str, state: WorkflowState) -> WorkflowState:
        """Persist or store a workflow state snapshot.

        Args:
            workflow_id: Unique workflow instance identifier.
            state: WorkflowState instance to store.

        Returns:
            Saved WorkflowState instance.

        Raises:
            WorkflowValidationError: If workflow_id is empty.
        """
        if not workflow_id or not workflow_id.strip():
            raise WorkflowValidationError(
                "Workflow ID cannot be empty", workflow_id="unknown"
            )

        state.workflow_id = workflow_id
        state.updated_at = datetime.now(UTC)
        self._states[workflow_id] = state
        return state

    def load_state(self, workflow_id: str) -> WorkflowState:
        """Load the persisted state of a workflow.

        Args:
            workflow_id: Unique workflow instance identifier.

        Returns:
            Loaded WorkflowState instance.

        Raises:
            WorkflowNotFoundError: If state is not found.
        """
        if workflow_id not in self._states:
            raise WorkflowNotFoundError(
                f"State for workflow '{workflow_id}' not found",
                workflow_id=workflow_id,
            )
        return self._states[workflow_id]

    def update_state(
        self,
        workflow_id: str,
        new_status: WorkflowStatus,
        triggering_event: str = "state_update",
        state_data: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowState:
        """Transition workflow to a new status and record state history.

        Args:
            workflow_id: Unique workflow instance identifier.
            new_status: Target WorkflowStatus.
            triggering_event: Event or action description triggering the change.
            state_data: Optional state variables dictionary to merge.
            metadata: Optional additional history metadata.

        Returns:
            Updated WorkflowState instance.

        Raises:
            WorkflowNotFoundError: If workflow state is not registered.
            WorkflowStateError: If transition is invalid.
        """
        state = self.load_state(workflow_id)
        current = state.current_state

        # Validate allowed transition
        validate_state_transition(workflow_id, current, new_status)

        # Record history entry
        now = datetime.now(UTC)
        history_entry = StateHistoryEntry(
            previous_state=current,
            current_state=new_status,
            timestamp=now,
            triggering_event=triggering_event,
            metadata=metadata or {},
        )

        state.history.append(history_entry)
        state.current_state = new_status
        state.updated_at = now

        if state_data:
            state.state_data.update(state_data)

        return state

    def delete_state(self, workflow_id: str) -> bool:
        """Delete persisted workflow state.

        Args:
            workflow_id: Unique workflow instance identifier.

        Returns:
            True if state existed and was removed, False otherwise.
        """
        if workflow_id in self._states:
            del self._states[workflow_id]
            return True
        return False

    def get_history(self, workflow_id: str) -> list[StateHistoryEntry]:
        """Retrieve full state transition audit history for a workflow.

        Args:
            workflow_id: Unique workflow instance identifier.

        Returns:
            List of StateHistoryEntry items.

        Raises:
            WorkflowNotFoundError: If state is not found.
        """
        state = self.load_state(workflow_id)
        return list(state.history)

    def restore_state(
        self,
        workflow_id: str,
        history_index: int = -1,
    ) -> WorkflowState:
        """Restore workflow state to a historical checkpoint entry.

        Args:
            workflow_id: Unique workflow instance identifier.
            history_index: List index in state.history to restore (-1 for latest).

        Returns:
            Restored WorkflowState instance.

        Raises:
            WorkflowNotFoundError: If workflow state is not found.
            WorkflowStateError: If history_index is invalid or history is empty.
        """
        state = self.load_state(workflow_id)
        if not state.history:
            raise WorkflowStateError(
                f"Cannot restore state for workflow '{workflow_id}': history is empty",
                workflow_id=workflow_id,
            )

        try:
            target_entry = state.history[history_index]
        except IndexError as err:
            raise WorkflowStateError(
                f"Invalid history_index {history_index} for workflow '{workflow_id}'",
                workflow_id=workflow_id,
            ) from err

        prev = state.current_state
        state.current_state = target_entry.current_state
        now = datetime.now(UTC)
        state.updated_at = now

        # Add restoration record to history
        restore_entry = StateHistoryEntry(
            previous_state=prev,
            current_state=target_entry.current_state,
            timestamp=now,
            triggering_event=f"restored_from_index_{history_index}",
            metadata={"restored_index": history_index},
        )
        state.history.append(restore_entry)

        return state
