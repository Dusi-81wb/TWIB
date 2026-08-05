"""Registration response Pydantic schema.

Defines the response payload returned upon successful user registration.
"""

from __future__ import annotations

from app.schemas.auth.login_response import LoginResponse


class RegisterResponse(LoginResponse):
    """Response model for user registration."""

    pass
