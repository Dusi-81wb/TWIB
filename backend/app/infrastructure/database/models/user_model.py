"""User ORM model.

This module defines :class:`UserModel`, the SQLAlchemy 2.0 ORM persistence
mapping for the User aggregate root (:class:`app.domain.users.user.User`).
It includes database column definitions, indices, and lazy-loading async
relationships to owned organizations/workspaces and organization/workspace
memberships.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import Index, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.infrastructure.database.models.organization_model import (
        OrganizationMemberModel,
        OrganizationModel,
    )
    from app.infrastructure.database.models.workspace_model import (
        WorkspaceMemberModel,
        WorkspaceModel,
    )


class UserModel(BaseModel):
    """SQLAlchemy ORM model for the User aggregate root.

    Maps user persistence attributes and relationships. Does not contain any
    domain logic or authentication details.

    Attributes:
        email: Unique, indexed user email address.
        display_name: User display name.
        status: Lifecycle state (e.g. pending, active, suspended, disabled, deleted).
        role: Organization-level role (e.g. owner, admin, member, viewer).
        metadata_json: Key/value JSON metadata map (column name: 'metadata').
        owned_organizations: Organizations owned by this user.
        organization_memberships: Organization memberships for this user.
        owned_workspaces: Workspaces owned by this user.
        workspace_memberships: Workspace memberships for this user.
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        index=True,
        nullable=False,
    )
    role: Mapped[str] = mapped_column(
        String(50),
        default="member",
        nullable=False,
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
    )

    # Relationships (lazy="selectin" for async SQLAlchemy compliance)
    owned_organizations: Mapped[list[OrganizationModel]] = relationship(
        "OrganizationModel",
        back_populates="owner",
        foreign_keys="OrganizationModel.owner_id",
        lazy="selectin",
    )
    organization_memberships: Mapped[list[OrganizationMemberModel]] = relationship(
        "OrganizationMemberModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    owned_workspaces: Mapped[list[WorkspaceModel]] = relationship(
        "WorkspaceModel",
        back_populates="owner",
        foreign_keys="WorkspaceModel.owner_id",
        lazy="selectin",
    )
    workspace_memberships: Mapped[list[WorkspaceMemberModel]] = relationship(
        "WorkspaceMemberModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (Index("ix_users_email_status", "email", "status"),)
