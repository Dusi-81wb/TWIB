"""Create workspace request Pydantic schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CreateWorkspaceRequest(BaseModel):
    """Request model for creating a new workspace.

    Attributes:
        organization_id: Parent organization UUID identity.
        name: Name of the workspace.
        slug: Optional URL-friendly slug. If omitted, generated from name.
        description: Optional workspace description.
    """

    organization_id: str = Field(
        ...,
        description="Parent organization UUID identity.",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Workspace name.",
    )
    slug: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
        description="URL-friendly workspace slug.",
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Workspace description.",
    )
