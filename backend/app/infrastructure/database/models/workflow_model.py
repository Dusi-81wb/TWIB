"""Workflow SQLAlchemy 2.0 ORM Models.

Defines persistence mappings for:
- WorkflowModel
- WorkflowExecutionModel
- WorkflowCheckpointModel
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.models.base_model import BaseModel


class WorkflowModel(BaseModel):
    """SQLAlchemy ORM persistence mapping for Workflow aggregate."""

    __tablename__ = "workflows"

    workspace_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    user_request: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="created",
        nullable=False,
        index=True,
    )
    graph_definition: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=lambda: {"nodes": [], "edges": []},
        nullable=False,
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
    )

    __table_args__ = (
        Index("ix_workflows_workspace_status", "workspace_id", "status"),
    )


class WorkflowExecutionModel(BaseModel):
    """SQLAlchemy ORM persistence mapping for WorkflowExecution aggregate."""

    __tablename__ = "workflow_executions"

    workflow_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="created",
        nullable=False,
        index=True,
    )
    context: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    node_states: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    step_outputs: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    duration_seconds: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
    )

    __table_args__ = (
        Index("ix_workflow_executions_wf_status", "workflow_id", "status"),
    )


class WorkflowCheckpointModel(BaseModel):
    """SQLAlchemy ORM persistence mapping for WorkflowCheckpoint entity."""

    __tablename__ = "workflow_checkpoints"

    workflow_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    execution_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workflow_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    checkpoint_type: Mapped[str] = mapped_column(
        String(50),
        default="human_approval",
        nullable=False,
    )
    approval_status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
    )
    data_to_review: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    state_snapshot: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    assigned_role: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    requested_by: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    reviewed_by: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    comments: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        Index("ix_workflow_checkpoints_status", "workflow_id", "approval_status"),
    )
