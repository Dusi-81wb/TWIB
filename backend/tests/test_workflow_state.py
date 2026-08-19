"""Tests for Workflow State Management implementation."""

import pytest

from app.workflows import (
    WorkflowState,
    WorkflowStateError,
    WorkflowStateManager,
    WorkflowStatus,
    validate_state_transition,
)


def test_valid_state_transitions() -> None:
    wf_id = "wf-test-123"
    assert (
        validate_state_transition(wf_id, WorkflowStatus.CREATED, WorkflowStatus.READY)
        is True
    )
    assert (
        validate_state_transition(wf_id, WorkflowStatus.READY, WorkflowStatus.RUNNING)
        is True
    )
    assert (
        validate_state_transition(wf_id, WorkflowStatus.RUNNING, WorkflowStatus.PAUSED)
        is True
    )
    assert (
        validate_state_transition(
            wf_id, WorkflowStatus.RUNNING, WorkflowStatus.WAITING_FOR_APPROVAL
        )
        is True
    )
    assert (
        validate_state_transition(wf_id, WorkflowStatus.PAUSED, WorkflowStatus.RUNNING)
        is True
    )
    assert (
        validate_state_transition(
            wf_id, WorkflowStatus.RUNNING, WorkflowStatus.COMPLETED
        )
        is True
    )


def test_invalid_state_transitions() -> None:
    wf_id = "wf-test-123"
    # COMPLETED -> RUNNING ❌
    with pytest.raises(WorkflowStateError):
        validate_state_transition(
            wf_id, WorkflowStatus.COMPLETED, WorkflowStatus.RUNNING
        )

    # FAILED -> RUNNING ❌
    with pytest.raises(WorkflowStateError):
        validate_state_transition(wf_id, WorkflowStatus.FAILED, WorkflowStatus.RUNNING)

    # CANCELLED -> RUNNING ❌
    with pytest.raises(WorkflowStateError):
        validate_state_transition(
            wf_id, WorkflowStatus.CANCELLED, WorkflowStatus.RUNNING
        )


def test_workflow_state_manager_crud() -> None:
    manager = WorkflowStateManager()
    wf_id = "wf-state-001"

    initial_state = WorkflowState(
        workflow_id=wf_id,
        current_state=WorkflowStatus.CREATED,
        state_data={"param": "value1"},
    )

    saved = manager.save_state(wf_id, initial_state)
    assert saved.workflow_id == wf_id

    loaded = manager.load_state(wf_id)
    assert loaded.current_state == WorkflowStatus.CREATED
    assert loaded.state_data["param"] == "value1"

    # Update state
    updated = manager.update_state(
        wf_id,
        new_status=WorkflowStatus.RUNNING,
        triggering_event="start_execution",
        state_data={"step": "1"},
    )
    assert updated.current_state == WorkflowStatus.RUNNING
    assert len(updated.history) == 1
    assert updated.history[0].previous_state == WorkflowStatus.CREATED
    assert updated.history[0].current_state == WorkflowStatus.RUNNING

    # Audit History
    history = manager.get_history(wf_id)
    assert len(history) == 1

    # Delete State
    assert manager.delete_state(wf_id) is True
    assert manager.delete_state(wf_id) is False


def test_workflow_state_restoration() -> None:
    manager = WorkflowStateManager()
    wf_id = "wf-restore-001"

    initial_state = WorkflowState(
        workflow_id=wf_id,
        current_state=WorkflowStatus.CREATED,
    )
    manager.save_state(wf_id, initial_state)

    manager.update_state(wf_id, WorkflowStatus.READY, triggering_event="validate")
    manager.update_state(wf_id, WorkflowStatus.RUNNING, triggering_event="start")
    manager.update_state(wf_id, WorkflowStatus.PAUSED, triggering_event="user_pause")

    # Restore to state at index 0 (which was READY)
    restored = manager.restore_state(wf_id, history_index=0)
    assert restored.current_state == WorkflowStatus.READY
