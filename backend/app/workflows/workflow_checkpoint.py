"""Workflow Checkpoint models and approval status enums.

Defines WorkflowCheckpoint data structures, CheckpointType, and ApprovalStatus enums.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ApprovalStatus(StrEnum):
    """Status of a human approval checkpoint review.

    Members:
        PENDING: Checkpoint is created and awaiting review.
        APPROVED: Human reviewer approved the checkpoint.
        REJECTED: Human reviewer rejected the checkpoint.
        CHANGES_REQUESTED: Human reviewer requested modifications.
    """

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"


class CheckpointType(StrEnum):
    """Categorization types for human approval checkpoints.

    Members:
        ARCHITECTURE_APPROVAL: Approval for system architecture specifications.
        RESEARCH_APPROVAL: Approval for domain research reports.
        DOCUMENTATION_APPROVAL: Approval for generated user/tech documentation.
        FINAL_APPROVAL: Final signoff before workflow completion.
    """

    ARCHITECTURE_APPROVAL = "architecture_approval"
    RESEARCH_APPROVAL = "research_approval"
    DOCUMENTATION_APPROVAL = "documentation_approval"
    FINAL_APPROVAL = "final_approval"


class WorkflowCheckpoint(BaseModel):
    """Structured human-in-the-loop approval checkpoint."""

    checkpoint_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique checkpoint identifier.",
    )
    workflow_id: str = Field(..., description="Target workflow identifier.")
    step_id: str | None = Field(
        default=None,
        description="Optional step or agent ID associated with checkpoint.",
    )
    checkpoint_type: CheckpointType | str = Field(
        default=CheckpointType.FINAL_APPROVAL,
        description="Type of approval checkpoint.",
    )
    approval_status: ApprovalStatus = Field(
        default=ApprovalStatus.PENDING,
        description="Current approval status.",
    )
    title: str = Field(..., description="Checkpoint title.")
    description: str = Field(
        default="", description="Detailed description of review item."
    )
    data_to_review: dict[str, Any] = Field(
        default_factory=dict,
        description="Payload or artifacts submitted for human inspection.",
    )
    assigned_role: str | None = Field(
        default=None,
        description="Required RBAC role authorized to approve/reject checkpoint.",
    )
    requested_by: str | None = Field(
        default=None,
        description="User or process ID that requested the checkpoint.",
    )
    reviewed_by: str | None = Field(
        default=None,
        description="User ID of the human reviewer who acted on the checkpoint.",
    )
    comments: str | None = Field(
        default=None,
        description="Reviewer feedback or rejection notes.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when checkpoint was created.",
    )
    reviewed_at: datetime | None = Field(
        default=None,
        description="Timestamp when reviewer acted on checkpoint.",
    )
