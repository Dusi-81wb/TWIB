"""Workspace ORM models.

This module defines :class:`WorkspaceModel` and :class:`WorkspaceMemberModel`,
the SQLAlchemy 2.0 ORM persistence mappings for the Workspace aggregate root
(:class:`app.domain.workspaces.workspace.Workspace`) and its
memberships (:class:`app.domain.workspaces.membership.WorkspaceMembership`).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.infrastructure.database.models.organization_model import (
        OrganizationModel,
    )
    from app.infrastructure.database.models.user_model import UserModel


class WorkspaceModel(BaseModel):
    """SQLAlchemy ORM model for the Workspace aggregate root.

    Attributes:
        organization_id: Foreign key referencing the parent organization.
        owner_id: Foreign key identity of the workspace owner.
        name: Workspace display name.
        slug: URL-friendly slug unique within the organization.
        description: Free-text workspace description.
        status: Lifecycle state (e.g. active, suspended, archived, deleted).
        settings_json: Key/value JSON workspace configuration (column name: 'settings').
        metadata_json: Key/value JSON metadata map (column name: 'metadata').
        organization: Parent organization relationship.
        owner: Workspace owner user relationship.
        memberships: Collection of workspace member records.
    """

    __tablename__ = "workspaces"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        default="",
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="active",
        index=True,
        nullable=False,
    )
    settings_json: Mapped[dict[str, Any]] = mapped_column(
        "settings",
        JSON,
        default=dict,
        nullable=False,
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
    )

    # Relationships (lazy="selectin" for async SQLAlchemy compliance)
    organization: Mapped[OrganizationModel] = relationship(
        "OrganizationModel",
        back_populates="workspaces",
        lazy="selectin",
    )
    owner: Mapped[UserModel] = relationship(
        "UserModel",
        back_populates="owned_workspaces",
        foreign_keys=[owner_id],
        lazy="selectin",
    )
    memberships: Mapped[list[WorkspaceMemberModel]] = relationship(
        "WorkspaceMemberModel",
        back_populates="workspace",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "slug",
            name="uq_workspace_org_slug",
        ),
        Index("ix_workspaces_org_slug", "organization_id", "slug"),
    )


class WorkspaceMemberModel(BaseModel):
    """SQLAlchemy ORM model for workspace memberships.

    Attributes:
        workspace_id: Foreign key referencing the parent workspace.
        user_id: Foreign key referencing the member user.
        role: Workspace membership role (e.g. owner, admin, member, viewer).
        status: Membership lifecycle status (e.g. active, inactive).
        joined_at: Timestamp when membership started (UTC).
        invitation_accepted: Whether the invitation was accepted.
        workspace: Parent workspace relationship.
        user: Member user relationship.
    """

    __tablename__ = "workspace_memberships"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    role: Mapped[str] = mapped_column(
        String(50),
        default="viewer",
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="active",
        nullable=False,
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    invitation_accepted: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Relationships
    workspace: Mapped[WorkspaceModel] = relationship(
        "WorkspaceModel",
        back_populates="memberships",
        lazy="selectin",
    )
    user: Mapped[UserModel] = relationship(
        "UserModel",
        back_populates="workspace_memberships",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint(
            "workspace_id",
            "user_id",
            name="uq_workspace_member_ws_user",
        ),
        Index("ix_workspace_members_ws_user", "workspace_id", "user_id"),
    )
