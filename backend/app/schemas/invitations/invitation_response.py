"""Invitation response Pydantic schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class InvitationResponse(BaseModel):
    """Response model representing a workspace invitation.

    Attributes:
        id: Invitation UUID identity string.
        workspace_id: Target workspace UUID string.
        email: Invitee email address.
        role: Assigned workspace role string.
        status: Invitation status (pending, accepted, rejected, expired).
        created_at: ISO 8601 UTC creation timestamp.
    """

    id: str = Field(..., description="Invitation UUID identity.")
    workspace_id: str = Field(..., description="Target workspace UUID identity.")
    email: str = Field(..., description="Invitee email address.")
    role: str = Field(..., description="Assigned workspace role.")
    status: str = Field(
        ...,
        description="Invitation status (pending, accepted, rejected, expired).",
    )
    created_at: str = Field(..., description="ISO 8601 UTC creation timestamp.")
