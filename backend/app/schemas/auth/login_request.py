"""Login request Pydantic schema.

Defines the request payload required for user login.
"""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login credentials payload."""

    email: EmailStr = Field(
        ...,
        description="User's registered email address.",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        min_length=1,
        description="User's account password.",
        examples=["SecretPassword123!"],
    )
