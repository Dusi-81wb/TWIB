"""Permission response Pydantic schemas.

Defines response models representing a user's granted permissions and roles.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class PermissionResponse(BaseModel):
    """Payload representing a user's effective roles and permissions."""

    user_id: str = Field(..., description="Unique UUID identity of the user.")
    organization_role: str | None = Field(
        default=None,
        description="User's primary organization role.",
    )
    workspace_roles: dict[str, str] = Field(
        default_factory=dict,
        description="Mapping of workspace IDs to user roles.",
    )
    permissions: list[str] = Field(
        default_factory=list,
        description="List of effective permission strings granted to the user.",
    )
