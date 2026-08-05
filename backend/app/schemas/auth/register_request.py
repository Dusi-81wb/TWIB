"""Registration request Pydantic schema.

Defines the request payload required for user registration.
"""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, model_validator


class RegisterRequest(BaseModel):
    """User registration request payload."""

    email: EmailStr = Field(
        ...,
        description="User's email address.",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        min_length=8,
        description="User's account password (minimum 8 characters).",
        examples=["SecretPassword123!"],
    )
    display_name: str | None = Field(
        default=None,
        description="Optional display name for the user.",
        examples=["Jane Doe"],
    )
    name: str | None = Field(
        default=None,
        description="Optional name alias for display_name.",
        examples=["Jane Doe"],
    )

    @model_validator(mode="after")
    def resolve_display_name(self) -> RegisterRequest:
        """Resolve display_name from name if display_name is omitted."""
        if not self.display_name and self.name:
            self.display_name = self.name
        return self

    @property
    def resolved_display_name(self) -> str:
        """Return the resolved display name string or fallback to email local part."""
        if self.display_name and self.display_name.strip():
            return self.display_name.strip()
        if self.name and self.name.strip():
            return self.name.strip()
        return self.email.split("@")[0]
