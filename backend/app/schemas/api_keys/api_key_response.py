"""API Key response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ApiKeyResponse(BaseModel):
    """Response payload containing API key metadata."""

    id: str = Field(..., description="Unique UUID identity of the API key.")
    workspace_id: str = Field(..., description="Owning workspace UUID.")
    name: str = Field(..., description="Display name of the API key.")
    prefix: str = Field(
        ...,
        description="Public prefix string (e.g. twib_live_a1b2c3d4).",
    )
    permissions: list[str] = Field(
        default_factory=list,
        description="Granted permission strings.",
    )
    created_at: str = Field(
        ...,
        description="Creation timestamp in ISO 8601 UTC format.",
    )
    expires_at: str | None = Field(
        default=None,
        description="Expiration timestamp, if set.",
    )
    last_used_at: str | None = Field(
        default=None,
        description="Last usage timestamp, if set.",
    )
    status: str = Field(
        ...,
        description="Status state: 'active', 'revoked', or 'expired'.",
    )


class CreatedApiKeyResponse(ApiKeyResponse):
    """Response payload returned ONLY upon creation containing plaintext key."""

    api_key: str = Field(
        ...,
        description="Full plaintext API key. SHOWN ONLY ONCE upon creation.",
        examples=["twib_live_a1b2c3d4_dGhpcy1pcy1hLXNlY3JldC1zdHJpbmc..."],
    )
