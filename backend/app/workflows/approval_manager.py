"""Approval Manager implementation.

Manages creation, RBAC authorization, human approval workflows, audit logging,
and workflow resumption across human-in-the-loop checkpoints.
"""

from __future__ import annotations

import contextlib
from datetime import UTC, datetime
from typing import Any

from app.authorization.roles import is_org_role_at_least, is_workspace_role_at_least
from app.services.audit.audit_service import AuditService
from app.workflows.workflow import Workflow
from app.workflows.workflow_checkpoint import (
    ApprovalStatus,
    CheckpointType,
    WorkflowCheckpoint,
)
from app.workflows.workflow_engine import WorkflowEngine
from app.workflows.workflow_exceptions import (
    WorkflowNotFoundError,
    WorkflowStateError,
    WorkflowValidationError,
)
from app.workflows.workflow_models import WorkflowStatus
from app.workflows.workflow_state_manager import WorkflowStateManager


class ApprovalManager:
    """Manager for Human Approval checkpoints and workflow pause/resume logic."""

    def __init__(
        self,
        engine: WorkflowEngine | None = None,
        state_manager: WorkflowStateManager | None = None,
        audit_service: AuditService | None = None,
    ) -> None:
        """Initialize ApprovalManager.

        Args:
            engine: Optional WorkflowEngine instance.
            state_manager: Optional WorkflowStateManager instance.
            audit_service: Optional AuditService instance.
        """
        self._engine = engine or WorkflowEngine()
        self._state_manager = state_manager or WorkflowStateManager()
        self._audit_service = audit_service or AuditService()
        self._checkpoints: dict[str, WorkflowCheckpoint] = {}

    def create_checkpoint(
        self,
        workflow_id: str,
        title: str,
        checkpoint_type: CheckpointType | str = CheckpointType.FINAL_APPROVAL,
        data_to_review: dict[str, Any] | None = None,
        description: str = "",
        assigned_role: str | None = None,
        step_id: str | None = None,
        requested_by: str | None = None,
    ) -> WorkflowCheckpoint:
        """Create a new human approval checkpoint for a workflow.

        Args:
            workflow_id: Target workflow identifier.
            title: Title description of the review checkpoint.
            checkpoint_type: Type of approval checkpoint.
            data_to_review: Payload data submitted for inspection.
            description: Detailed checkpoint explanation.
            assigned_role: Required RBAC role for approval.
            step_id: Optional step or agent identifier.
            requested_by: Optional requesting user ID.

        Returns:
            Created WorkflowCheckpoint instance.

        Raises:
            WorkflowValidationError: If title or workflow_id is empty.
        """
        if not workflow_id or not workflow_id.strip():
            raise WorkflowValidationError(
                "Workflow ID cannot be empty", workflow_id="unknown"
            )
        if not title or not title.strip():
            raise WorkflowValidationError(
                "Checkpoint title cannot be empty", workflow_id=workflow_id
            )

        checkpoint = WorkflowCheckpoint(
            workflow_id=workflow_id,
            title=title.strip(),
            checkpoint_type=checkpoint_type,
            data_to_review=data_to_review or {},
            description=description,
            assigned_role=assigned_role,
            step_id=step_id,
            requested_by=requested_by,
        )
        self._checkpoints[checkpoint.checkpoint_id] = checkpoint
        return checkpoint

    def get_checkpoint(self, checkpoint_id: str) -> WorkflowCheckpoint:
        """Load a checkpoint by its unique ID.

        Args:
            checkpoint_id: Unique checkpoint identifier.

        Returns:
            Loaded WorkflowCheckpoint instance.

        Raises:
            WorkflowNotFoundError: If checkpoint is not found.
        """
        if checkpoint_id not in self._checkpoints:
            raise WorkflowNotFoundError(
                f"Checkpoint '{checkpoint_id}' not found",
                workflow_id="unknown",
            )
        return self._checkpoints[checkpoint_id]

    def pause_for_approval(
        self, workflow_id: str, checkpoint_id: str
    ) -> WorkflowCheckpoint:
        """Pause a workflow for human approval at a checkpoint.

        Args:
            workflow_id: Unique workflow identifier.
            checkpoint_id: Unique checkpoint identifier.

        Returns:
            Updated WorkflowCheckpoint instance.
        """
        checkpoint = self.get_checkpoint(checkpoint_id)

        import contextlib

        with contextlib.suppress(Exception):
            self._state_manager.update_state(
                workflow_id,
                WorkflowStatus.WAITING_FOR_APPROVAL,
                triggering_event=f"checkpoint_pause_{checkpoint.checkpoint_type}",
                metadata={"checkpoint_id": checkpoint_id},
            )

        with contextlib.suppress(Exception):
            wf = self._engine.load_workflow(workflow_id)
            wf.update_status(WorkflowStatus.WAITING_FOR_APPROVAL)

        return checkpoint

    def approve(
        self,
        checkpoint_id: str,
        user_id: str,
        user_roles: list[str] | None = None,
        comments: str | None = None,
    ) -> WorkflowCheckpoint:
        """Approve a pending human checkpoint.

        Args:
            checkpoint_id: Unique checkpoint identifier.
            user_id: ID of the human reviewer.
            user_roles: Roles held by the user for RBAC authorization.
            comments: Optional reviewer notes.

        Returns:
            Approved WorkflowCheckpoint instance.

        Raises:
            WorkflowValidationError: If user is unauthorized by RBAC rules.
        """
        checkpoint = self.get_checkpoint(checkpoint_id)
        self._authorize_user(checkpoint, user_roles)

        checkpoint.approval_status = ApprovalStatus.APPROVED
        checkpoint.reviewed_by = user_id
        checkpoint.reviewed_at = datetime.now(UTC)
        checkpoint.comments = comments

        return checkpoint

    def reject(
        self,
        checkpoint_id: str,
        user_id: str,
        user_roles: list[str] | None = None,
        comments: str | None = None,
    ) -> WorkflowCheckpoint:
        """Reject a pending human checkpoint.

        Args:
            checkpoint_id: Unique checkpoint identifier.
            user_id: ID of the human reviewer.
            user_roles: Roles held by the user for RBAC authorization.
            comments: Optional rejection reason.

        Returns:
            Rejected WorkflowCheckpoint instance.

        Raises:
            WorkflowValidationError: If user is unauthorized by RBAC rules.
        """
        checkpoint = self.get_checkpoint(checkpoint_id)
        self._authorize_user(checkpoint, user_roles)

        checkpoint.approval_status = ApprovalStatus.REJECTED
        checkpoint.reviewed_by = user_id
        checkpoint.reviewed_at = datetime.now(UTC)
        checkpoint.comments = comments

        # Transition workflow to FAILED status
        with contextlib.suppress(Exception):
            self._state_manager.update_state(
                checkpoint.workflow_id,
                WorkflowStatus.FAILED,
                triggering_event="checkpoint_rejected",
                metadata={"checkpoint_id": checkpoint_id, "comments": comments},
            )

        return checkpoint

    def request_changes(
        self,
        checkpoint_id: str,
        user_id: str,
        user_roles: list[str] | None = None,
        feedback: str | None = None,
    ) -> WorkflowCheckpoint:
        """Request changes on a pending human checkpoint.

        Args:
            checkpoint_id: Unique checkpoint identifier.
            user_id: ID of the human reviewer.
            user_roles: Roles held by the user for RBAC authorization.
            feedback: Required or optional feedback notes for requested changes.

        Returns:
            Updated WorkflowCheckpoint instance.

        Raises:
            WorkflowValidationError: If user is unauthorized by RBAC rules.
        """
        checkpoint = self.get_checkpoint(checkpoint_id)
        self._authorize_user(checkpoint, user_roles)

        checkpoint.approval_status = ApprovalStatus.CHANGES_REQUESTED
        checkpoint.reviewed_by = user_id
        checkpoint.reviewed_at = datetime.now(UTC)
        checkpoint.comments = feedback

        return checkpoint

    def resume(self, workflow_id: str, checkpoint_id: str) -> Workflow:
        """Resume a workflow after checkpoint approval.

        Args:
            workflow_id: Unique workflow identifier.
            checkpoint_id: Unique checkpoint identifier.

        Returns:
            Resumed Workflow domain instance.

        Raises:
            WorkflowStateError: If checkpoint is not approved.
        """
        checkpoint = self.get_checkpoint(checkpoint_id)
        if checkpoint.approval_status != ApprovalStatus.APPROVED:
            raise WorkflowStateError(
                f"Cannot resume workflow '{workflow_id}': checkpoint status is "
                f"'{checkpoint.approval_status}', must be APPROVED",
                workflow_id=workflow_id,
            )

        # Transition state back to RUNNING
        with contextlib.suppress(Exception):
            self._state_manager.update_state(
                workflow_id,
                WorkflowStatus.RUNNING,
                triggering_event="checkpoint_resumed",
            )

        wf = self._engine.load_workflow(workflow_id)
        wf.update_status(WorkflowStatus.RUNNING)
        return wf

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _authorize_user(
        checkpoint: WorkflowCheckpoint, user_roles: list[str] | None
    ) -> None:
        """Validate RBAC authorization for acting on a checkpoint."""
        if not checkpoint.assigned_role:
            return

        req_role = checkpoint.assigned_role.lower()

        if not user_roles:
            err_msg = f"User lacks required role '{req_role}' for checkpoint"
            raise WorkflowValidationError(
                err_msg,
                workflow_id=checkpoint.workflow_id,
            )

        authorized = False
        for role in user_roles:
            role_clean = role.lower()
            if (
                role_clean == req_role
                or is_org_role_at_least(role_clean, req_role)
                or is_workspace_role_at_least(role_clean, req_role)
            ):
                authorized = True
                break

        if not authorized:
            err_msg = f"User roles {user_roles} unauthorized for role '{req_role}'"
            raise WorkflowValidationError(
                err_msg,
                workflow_id=checkpoint.workflow_id,
            )
