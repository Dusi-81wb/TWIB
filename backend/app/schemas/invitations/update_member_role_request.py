"""Update member role request Pydantic schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class UpdateMemberRoleRequest(BaseModel):
    """Request model for updating a workspace member's role.

    Attributes:
        role: New workspace role (owner, admin, editor, contributor, viewer).
    """

    role: str = Field(
        ...,
        description="New workspace role (owner, admin, editor, contributor, viewer).",
    )
