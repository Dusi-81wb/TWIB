"""Refresh token request Pydantic schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RefreshRequest(BaseModel):
    """Payload for refreshing an access token."""

    refresh_token: str = Field(
        ...,
        description="Active refresh token string.",
        examples=["dGhpcy1pcy1hLXJlZnJlc2gtdG9rZW4..."],
    )
