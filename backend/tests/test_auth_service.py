"""Unit tests for AuthenticationService registration and login logic."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.users.exceptions import EmailAlreadyAssigned
from app.services.auth.authentication_service import AuthenticationService


@pytest.mark.asyncio
async def test_register_user_success() -> None:
    """Test successful user registration in AuthenticationService."""
    mock_user_repo = AsyncMock()
    mock_user_repo.find_by_email.return_value = None
    mock_user_repo.save = AsyncMock()

    mock_uow = MagicMock()
    mock_uow.users = mock_user_repo
    mock_uow.commit = AsyncMock()
    mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
    mock_uow.__aexit__ = AsyncMock(return_value=None)

    mock_hasher = MagicMock()
    mock_hasher.hash_password.return_value = "$argon2id$v=19$m=65536,t=3,p=4$fakehash"

    mock_jwt = MagicMock()
    mock_jwt.create_access_token.return_value = "mock_jwt_access_token"

    mock_settings = MagicMock()
    mock_settings.access_token_expire_minutes = 30

    service = AuthenticationService(
        unit_of_work=mock_uow,
        password_hasher=mock_hasher,
        jwt_helper=mock_jwt,
        settings=mock_settings,
    )

    result = await service.register_user(
        email="newuser@example.com",
        password="SecretPassword123!",  # noqa: S106
        display_name="New User",
    )

    assert result["access_token"] == "mock_jwt_access_token"  # noqa: S105
    assert result["token_type"] == "bearer"  # noqa: S105
    assert result["user"]["email"] == "newuser@example.com"
    assert result["user"]["display_name"] == "New User"
    assert result["user"]["role"] == "member"
    assert result["user"]["status"] == "active"
    mock_user_repo.save.assert_called_once()
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_register_user_duplicate_email() -> None:
    """Test user registration error when email is already assigned."""
    existing_user = MagicMock()

    mock_user_repo = AsyncMock()
    mock_user_repo.find_by_email.return_value = existing_user

    mock_uow = MagicMock()
    mock_uow.users = mock_user_repo
    mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
    mock_uow.__aexit__ = AsyncMock(return_value=None)

    service = AuthenticationService(unit_of_work=mock_uow)

    with pytest.raises(EmailAlreadyAssigned) as exc_info:
        await service.register_user(
            email="existing@example.com",
            password="SecretPassword123!",  # noqa: S106
        )

    assert "already registered" in str(exc_info.value)
