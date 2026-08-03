"""Refresh token response Pydantic schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RefreshResponse(BaseModel):
    """Payload returned upon successful access token refresh."""

    access_token: str = Field(..., description="Newly issued JWT access token string.")
    refresh_token: str = Field(..., description="Newly rotated refresh token string.")
    token_type: str = Field(
        default="bearer",
        description="Token type.",
        examples=["bearer"],
    )
    expires_in: int = Field(
        ...,
        description="Access token expiration lifetime in seconds.",
        examples=[1800],
    )
