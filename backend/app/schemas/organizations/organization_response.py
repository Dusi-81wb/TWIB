"""Organization response Pydantic schemas.

Contains response models returned by organization management endpoints.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class OrganizationMemberResponse(BaseModel):
    """Response model for an organization member.

    Attributes:
        user_id: Member user UUID string.
        role: Role string (owner, admin, member, viewer).
        joined_at: ISO 8601 UTC timestamp.
        status: Membership status string.
    """

    user_id: str = Field(..., description="Member user UUID string.")
    role: str = Field(..., description="Member role (owner, admin, member, viewer).")
    joined_at: str = Field(..., description="ISO 8601 UTC timestamp.")
    status: str = Field(..., description="Membership status.")


class OrganizationResponse(BaseModel):
    """Response payload representing an individual organization.

    Attributes:
        id: Organization UUID identity.
        name: Organization name.
        slug: URL-friendly slug.
        owner_id: Owner user UUID identity.
        status: Lifecycle status.
        subscription_plan: Subscription plan string.
        created_at: ISO 8601 UTC creation timestamp.
        updated_at: ISO 8601 UTC last-update timestamp.
        metadata: Key/value metadata dictionary.
        members: List of organization members.
    """

    id: str = Field(..., description="Organization UUID identity.")
    name: str = Field(..., description="Organization name.")
    slug: str = Field(..., description="URL-friendly organization slug.")
    owner_id: str = Field(..., description="Owner user UUID identity.")
    status: str = Field(
        ...,
        description="Lifecycle status (pending, active, suspended, archived, deleted).",
    )
    subscription_plan: str = Field(
        ...,
        description="Subscription plan (free, starter, pro, enterprise).",
    )
    created_at: str = Field(..., description="ISO 8601 UTC creation timestamp.")
    updated_at: str = Field(..., description="ISO 8601 UTC last-update timestamp.")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Key/value metadata dictionary.",
    )
    members: list[OrganizationMemberResponse] = Field(
        default_factory=list,
        description="List of organization members.",
    )


class OrganizationListResponse(BaseModel):
    """Paginated list response containing organization entries."""

    items: list[OrganizationResponse] = Field(
        ..., description="List of organization items."
    )
    total: int = Field(..., description="Total matching organization count.")
    limit: int = Field(..., description="Maximum items per page.")
    offset: int = Field(..., description="Page offset index.")
