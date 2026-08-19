"""User update request Pydantic schemas.

Contains the request models for self-service profile updates and
admin-level user updates.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class UpdateProfileRequest(BaseModel):
    """Self-service profile update request.

    Users may update only their own display name and email via
    ``PATCH /api/v1/users/me``.

    Attributes:
        display_name: Optional new display name.
        email: Optional new email address.
    """

    display_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="New display name.",
    )
    email: str | None = Field(
        default=None,
        min_length=3,
        max_length=320,
        description="New email address.",
    )


class UpdateUserRequest(BaseModel):
    """Admin-level user update request.

    Admins may update a user's display name, email, role, and status
    via ``PATCH /api/v1/users/{id}``.

    Attributes:
        display_name: Optional new display name.
        email: Optional new email address.
        role: Optional new role string.
        status: Optional new status string.
    """

    display_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="New display name.",
    )
    email: str | None = Field(
        default=None,
        min_length=3,
        max_length=320,
        description="New email address.",
    )
    role: str | None = Field(
        default=None,
        description="New role (owner, admin, member, viewer).",
    )
    status: str | None = Field(
        default=None,
        description=("New status (pending, active, suspended, disabled, deleted)."),
    )
