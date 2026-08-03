"""Create organization request Pydantic schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CreateOrganizationRequest(BaseModel):
    """Request model for creating a new organization.

    Attributes:
        name: Name of the organization.
        slug: Optional URL-friendly slug. If omitted, generated from name.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Organization name.",
    )
    slug: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
        description="URL-friendly organization slug.",
    )
