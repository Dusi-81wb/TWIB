"""Create invitation request Pydantic schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CreateInvitationRequest(BaseModel):
    """Request model for creating a new workspace invitation.

    Attributes:
        workspace_id: Target workspace UUID identity.
        email: Invitee email address.
        role: Assigned workspace role (owner, admin, editor, contributor, viewer).
    """

    workspace_id: str = Field(
        ...,
        description="Target workspace UUID identity.",
    )
    email: str = Field(
        ...,
        min_length=3,
        max_length=320,
        description="Invitee email address.",
    )
    role: str = Field(
        default="viewer",
        description=(
            "Assigned workspace role (owner, admin, editor, contributor, viewer)."
        ),
    )
