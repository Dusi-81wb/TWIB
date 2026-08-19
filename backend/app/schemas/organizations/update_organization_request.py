"""Update organization request Pydantic schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class UpdateOrganizationRequest(BaseModel):
    """Request model for updating an existing organization.

    Attributes:
        name: Optional new organization name.
        slug: Optional new URL-friendly slug.
        subscription_plan: Optional new subscription plan.
        status: Optional new lifecycle status.
    """

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="New organization name.",
    )
    slug: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
        description="New URL-friendly slug.",
    )
    subscription_plan: str | None = Field(
        default=None,
        description="New subscription plan (free, starter, pro, enterprise).",
    )
    status: str | None = Field(
        default=None,
        description="New status (pending, active, suspended, archived, deleted).",
    )
