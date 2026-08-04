"""Tests for ApprovalManager and WorkflowCheckpoint implementation."""

import pytest

from app.workflows import (
    ApprovalManager,
    ApprovalStatus,
    CheckpointType,
    WorkflowEngine,
    WorkflowState,
    WorkflowStateError,
    WorkflowStateManager,
    WorkflowStatus,
    WorkflowValidationError,
)


def test_approval_manager_create_and_pause() -> None:
    engine = WorkflowEngine()
    state_manager = WorkflowStateManager()
    approval_mgr = ApprovalManager(engine=engine, state_manager=state_manager)

    wf = engine.create_workflow("Checkpoint Test WF", "Goal description")
    state_manager.save_state(
        wf.workflow_id,
        state_manager._states.get(wf.workflow_id)
        or WorkflowState(
            workflow_id=wf.workflow_id, current_state=WorkflowStatus.RUNNING
        ),
    )

    cp = approval_mgr.create_checkpoint(
        workflow_id=wf.workflow_id,
        title="Architecture Review",
        checkpoint_type=CheckpointType.ARCHITECTURE_APPROVAL,
        data_to_review={"arch_diagram": "url_to_diag"},
        assigned_role="admin",
    )

    assert cp.checkpoint_id is not None
    assert cp.approval_status == ApprovalStatus.PENDING
    assert cp.assigned_role == "admin"

    paused_cp = approval_mgr.pause_for_approval(wf.workflow_id, cp.checkpoint_id)
    assert paused_cp.checkpoint_id == cp.checkpoint_id
    assert (
        state_manager.load_state(wf.workflow_id).current_state
        == WorkflowStatus.WAITING_FOR_APPROVAL
    )


def test_approval_manager_approve_and_resume() -> None:
    engine = WorkflowEngine()
    state_manager = WorkflowStateManager()
    approval_mgr = ApprovalManager(engine=engine, state_manager=state_manager)

    wf = engine.create_workflow("Approve WF", "Approve test")
    state_manager.save_state(
        wf.workflow_id,
        WorkflowState(workflow_id=wf.workflow_id, current_state=WorkflowStatus.CREATED),
    )
    state_manager.update_state(
        wf.workflow_id, WorkflowStatus.RUNNING, triggering_event="start"
    )

    cp = approval_mgr.create_checkpoint(
        workflow_id=wf.workflow_id,
        title="Final Review",
        checkpoint_type=CheckpointType.FINAL_APPROVAL,
        assigned_role="editor",
    )

    approval_mgr.pause_for_approval(wf.workflow_id, cp.checkpoint_id)

    # Unauthorized role check
    with pytest.raises(WorkflowValidationError):
        approval_mgr.approve(cp.checkpoint_id, user_id="user-1", user_roles=["viewer"])

    # Authorized approval
    approved_cp = approval_mgr.approve(
        cp.checkpoint_id,
        user_id="user-admin",
        user_roles=["editor"],
        comments="Looks good to deploy!",
    )
    assert approved_cp.approval_status == ApprovalStatus.APPROVED
    assert approved_cp.reviewed_by == "user-admin"

    # Resume workflow
    resumed_wf = approval_mgr.resume(wf.workflow_id, cp.checkpoint_id)
    assert resumed_wf.workflow_status == WorkflowStatus.RUNNING


def test_approval_manager_reject_and_request_changes() -> None:
    engine = WorkflowEngine()
    state_manager = WorkflowStateManager()
    approval_mgr = ApprovalManager(engine=engine, state_manager=state_manager)

    wf = engine.create_workflow("Reject WF", "Reject test")
    state_manager.save_state(
        wf.workflow_id,
        WorkflowState(workflow_id=wf.workflow_id, current_state=WorkflowStatus.RUNNING),
    )

    cp1 = approval_mgr.create_checkpoint(wf.workflow_id, "Check 1")
    cp2 = approval_mgr.create_checkpoint(wf.workflow_id, "Check 2")

    # Request changes
    changes_cp = approval_mgr.request_changes(
        cp1.checkpoint_id,
        user_id="user-2",
        feedback="Please add scalability section",
    )
    assert changes_cp.approval_status == ApprovalStatus.CHANGES_REQUESTED

    # Cannot resume when changes requested
    with pytest.raises(WorkflowStateError):
        approval_mgr.resume(wf.workflow_id, cp1.checkpoint_id)

    # Reject checkpoint
    rejected_cp = approval_mgr.reject(
        cp2.checkpoint_id,
        user_id="user-2",
        comments="Rejected due to missing security plan",
    )
    assert rejected_cp.approval_status == ApprovalStatus.REJECTED
    assert (
        state_manager.load_state(wf.workflow_id).current_state == WorkflowStatus.FAILED
    )
