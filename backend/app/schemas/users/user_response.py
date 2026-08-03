"""User response Pydantic schemas.

Contains the response models returned by the user management endpoints.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    """Response payload representing an individual user.

    Attributes:
        id: User UUID string.
        email: User email address.
        display_name: User display name.
        role: User role string (owner, admin, member, viewer).
        status: User lifecycle status string.
        created_at: ISO 8601 UTC creation timestamp.
        updated_at: ISO 8601 UTC last-update timestamp.
        metadata: User metadata dictionary.
    """

    id: str = Field(..., description="User UUID identity.")
    email: str = Field(..., description="User email address.")
    display_name: str = Field(..., description="User display name.")
    role: str = Field(..., description="User role (owner, admin, member, viewer).")
    status: str = Field(
        ...,
        description="User status (pending, active, suspended, disabled, deleted).",
    )
    created_at: str = Field(..., description="ISO 8601 UTC creation timestamp.")
    updated_at: str = Field(..., description="ISO 8601 UTC last-update timestamp.")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="User metadata dictionary.",
    )


class UserListResponse(BaseModel):
    """Paginated user list response.

    Attributes:
        items: List of user response objects.
        total: Total number of matching users.
        limit: Maximum items per page.
        offset: Page offset index.
    """

    items: list[UserResponse] = Field(..., description="List of user items.")
    total: int = Field(..., description="Total matching user count.")
    limit: int = Field(..., description="Maximum items per page.")
    offset: int = Field(..., description="Page offset index.")
