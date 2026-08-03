"""Login and logout response Pydantic schemas.

Defines the response payloads returned upon successful login and logout operations.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class UserInfoResponse(BaseModel):
    """Authenticated user summary returned in login responses."""

    id: str = Field(..., description="Unique UUID identity of the user.")
    email: str = Field(..., description="User's email address.")
    display_name: str = Field(..., description="User's display name.")
    role: str = Field(..., description="User's platform role.")
    status: str = Field(..., description="User's account status.")


class LoginResponse(BaseModel):
    """Successful login authentication payload."""

    access_token: str = Field(..., description="JWT access token string.")
    refresh_token: str | None = Field(
        default=None,
        description="Refresh token string for session renewal.",
    )
    token_type: str = Field(
        default="bearer",
        description="Type of authentication token.",
        examples=["bearer"],
    )
    expires_in: int = Field(
        ...,
        description="Token lifetime in seconds.",
        examples=[1800],
    )
    user: UserInfoResponse = Field(..., description="Authenticated user details.")


class LogoutResponse(BaseModel):
    """Response payload for logout operation."""

    message: str = Field(
        default="Successfully logged out",
        description="Logout status message.",
        examples=["Successfully logged out"],
    )
