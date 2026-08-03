"""Organization ORM models.

This module defines :class:`OrganizationModel` and :class:`OrganizationMemberModel`,
the SQLAlchemy 2.0 ORM persistence mappings for the Organization aggregate root
(:class:`app.domain.organizations.organization.Organization`) and its
memberships (:class:`app.domain.organizations.membership.OrganizationMembership`).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.infrastructure.database.models.user_model import UserModel
    from app.infrastructure.database.models.workspace_model import WorkspaceModel


class OrganizationModel(BaseModel):
    """SQLAlchemy ORM model for the Organization aggregate root.

    Maps organization tenant boundary details, subscription plan, lifecycle status,
    owner relationship, membership child records, and child workspaces.

    Attributes:
        name: Organization display name.
        slug: URL-friendly unique slug.
        owner_id: Foreign key identity of the organization owner.
        status: Lifecycle state (e.g. pending, active, suspended, archived, deleted).
        subscription_plan: Active tier (e.g. free, starter, pro, enterprise).
        metadata_json: Key/value JSON metadata map (column name: 'metadata').
        owner: User relationship for the owner.
        memberships: Collection of organization member records.
        workspaces: Collection of child workspaces.
    """

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        index=True,
        nullable=False,
    )
    subscription_plan: Mapped[str] = mapped_column(
        String(50),
        default="free",
        nullable=False,
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
    )

    # Relationships (lazy="selectin" for async SQLAlchemy compliance)
    owner: Mapped[UserModel] = relationship(
        "UserModel",
        back_populates="owned_organizations",
        foreign_keys=[owner_id],
        lazy="selectin",
    )
    memberships: Mapped[list[OrganizationMemberModel]] = relationship(
        "OrganizationMemberModel",
        back_populates="organization",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    workspaces: Mapped[list[WorkspaceModel]] = relationship(
        "WorkspaceModel",
        back_populates="organization",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (Index("ix_organizations_slug_status", "slug", "status"),)


class OrganizationMemberModel(BaseModel):
    """SQLAlchemy ORM model for organization memberships.

    Maps the relationship between users and organizations, including roles,
    join timestamps, and invitation state.

    Attributes:
        organization_id: Foreign key referencing the organization.
        user_id: Foreign key referencing the user.
        role: Organization membership role (e.g. owner, admin, member, viewer).
        status: Membership lifecycle status (e.g. pending, active, inactive).
        joined_at: Timestamp when membership started (UTC).
        invitation_accepted: Whether the invitation was accepted.
        organization: Parent organization relationship.
        user: Member user relationship.
    """

    __tablename__ = "organization_memberships"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    role: Mapped[str] = mapped_column(
        String(50),
        default="member",
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
    organization: Mapped[OrganizationModel] = relationship(
        "OrganizationModel",
        back_populates="memberships",
        lazy="selectin",
    )
    user: Mapped[UserModel] = relationship(
        "UserModel",
        back_populates="organization_memberships",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "user_id",
            name="uq_org_member_org_user",
        ),
        Index("ix_org_members_org_user", "organization_id", "user_id"),
    )
