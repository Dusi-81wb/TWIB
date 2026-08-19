"""Update workspace request Pydantic schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class UpdateWorkspaceRequest(BaseModel):
    """Request model for updating an existing workspace.

    Attributes:
        name: Optional new workspace name.
        slug: Optional new URL-friendly slug.
        description: Optional new description.
        status: Optional new status string.
    """

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="New workspace name.",
    )
    slug: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
        description="New URL-friendly slug.",
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="New workspace description.",
    )
    status: str | None = Field(
        default=None,
        description="New status (active, suspended, archived, deleted).",
    )
