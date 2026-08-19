"""Workspace response Pydantic schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class WorkspaceMemberResponse(BaseModel):
    """Response model representing a member inside a workspace.

    Attributes:
        user_id: Member user UUID string.
        role: Member role string (owner, admin, member, viewer).
        joined_at: ISO 8601 UTC timestamp.
        status: Membership status string.
    """

    user_id: str = Field(..., description="Member user UUID string.")
    role: str = Field(..., description="Role string (owner, admin, member, viewer).")
    joined_at: str = Field(..., description="ISO 8601 UTC timestamp.")
    status: str = Field(..., description="Membership status string.")


class WorkspaceResponse(BaseModel):
    """Response payload representing an individual workspace.

    Attributes:
        id: Workspace UUID identity.
        organization_id: Parent organization UUID identity.
        name: Workspace name.
        slug: URL-friendly slug.
        description: Workspace description.
        owner_id: Owner user UUID identity.
        status: Lifecycle status (active, suspended, archived, deleted).
        created_at: ISO 8601 UTC creation timestamp.
        updated_at: ISO 8601 UTC last-update timestamp.
        metadata: Key/value metadata dictionary.
        members: List of workspace members.
    """

    id: str = Field(..., description="Workspace UUID identity.")
    organization_id: str = Field(..., description="Parent organization UUID identity.")
    name: str = Field(..., description="Workspace name.")
    slug: str = Field(..., description="URL-friendly workspace slug.")
    description: str = Field(default="", description="Workspace description.")
    owner_id: str = Field(..., description="Owner user UUID identity.")
    status: str = Field(
        ...,
        description="Lifecycle status (active, suspended, archived, deleted).",
    )
    created_at: str = Field(..., description="ISO 8601 UTC creation timestamp.")
    updated_at: str = Field(..., description="ISO 8601 UTC last-update timestamp.")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Key/value metadata dictionary.",
    )
    members: list[WorkspaceMemberResponse] = Field(
        default_factory=list,
        description="List of workspace members.",
    )


class WorkspaceListResponse(BaseModel):
    """Paginated list response containing workspace entries."""

    items: list[WorkspaceResponse] = Field(..., description="List of workspace items.")
    total: int = Field(..., description="Total matching workspace count.")
    limit: int = Field(..., description="Maximum items per page.")
    offset: int = Field(..., description="Page offset index.")
