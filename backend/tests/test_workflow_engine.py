"""Tests for Workflow Engine Core implementation."""

import pytest

from app.workflows import (
    WorkflowEngine,
    WorkflowNotFoundError,
    WorkflowStateError,
    WorkflowStatus,
    WorkflowStep,
    WorkflowValidationError,
)


def test_create_workflow_success() -> None:
    engine = WorkflowEngine()
    workflow = engine.create_workflow(
        workflow_name="Onboarding Pipeline",
        user_request="Build user onboarding workflow",
    )

    assert workflow.workflow_id is not None
    assert workflow.workflow_name == "Onboarding Pipeline"
    assert workflow.user_request == "Build user onboarding workflow"
    assert workflow.workflow_status == WorkflowStatus.CREATED
    assert len(workflow.execution_steps) == 0


def test_create_workflow_empty_name_or_request() -> None:
    engine = WorkflowEngine()
    with pytest.raises(WorkflowValidationError):
        engine.create_workflow(workflow_name="", user_request="test")

    with pytest.raises(WorkflowValidationError):
        engine.create_workflow(workflow_name="test", user_request="  ")


def test_load_workflow_success_and_not_found() -> None:
    engine = WorkflowEngine()
    wf = engine.create_workflow("Test WF", "Do something")

    loaded = engine.load_workflow(wf.workflow_id)
    assert loaded.workflow_id == wf.workflow_id

    with pytest.raises(WorkflowNotFoundError):
        engine.load_workflow("non-existent-id")


def test_validate_and_start_workflow() -> None:
    engine = WorkflowEngine()
    step = WorkflowStep(name="Plan Step", agent_id="planner")
    wf = engine.create_workflow(
        workflow_name="Pipeline",
        user_request="Plan and execution",
        steps=[step],
    )

    assert engine.validate_workflow(wf) is True
    assert wf.workflow_status == WorkflowStatus.READY

    started_wf = engine.start_workflow(wf.workflow_id)
    assert started_wf.workflow_status == WorkflowStatus.RUNNING


def test_cancel_workflow() -> None:
    engine = WorkflowEngine()
    wf = engine.create_workflow("Cancel Test", "Testing cancellation")
    cancelled_wf = engine.cancel_workflow(wf.workflow_id)
    assert cancelled_wf.workflow_status == WorkflowStatus.CANCELLED

    # Invalid state transition from CANCELLED
    with pytest.raises(WorkflowStateError):
        cancelled_wf.mark_running()


def test_workflow_lifecycle_status_transitions() -> None:
    engine = WorkflowEngine()
    wf = engine.create_workflow("Status Test", "Test statuses")

    wf.mark_ready()
    assert wf.workflow_status == WorkflowStatus.READY

    wf.mark_running()
    assert wf.workflow_status == WorkflowStatus.RUNNING

    wf.mark_paused()
    assert wf.workflow_status == WorkflowStatus.PAUSED

    wf.mark_completed()
    assert wf.workflow_status == WorkflowStatus.COMPLETED

    # Completed is a terminal state
    with pytest.raises(WorkflowStateError):
        wf.mark_running()
