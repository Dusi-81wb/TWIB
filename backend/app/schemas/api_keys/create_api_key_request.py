"""Create API Key request schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CreateApiKeyRequest(BaseModel):
    """Payload for creating a new workspace API key."""

    workspace_id: str = Field(
        ...,
        description="UUID identity of the workspace owning the key.",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    name: str = Field(
        ...,
        description="Human readable descriptive name for the API key.",
        examples=["Production Integration Key"],
    )
    environment: str = Field(
        default="live",
        description="Environment prefix: 'live' or 'test'.",
        examples=["live"],
    )
    expires_in_days: int | None = Field(
        default=None,
        description="Optional expiration lifetime in days.",
        examples=[90],
    )
    permissions: list[str] | None = Field(
        default=None,
        description="Optional scope permissions granted to the API key.",
    )
