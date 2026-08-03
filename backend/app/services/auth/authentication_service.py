"""Authentication application service.

Handles user login authentication, password verification against stored hashes,
JWT access token issuance, and logout handling.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from app.core.config import get_settings
from app.core.settings import ApplicationSettings
from app.domain.repositories.unit_of_work import UnitOfWork
from app.domain.users.status import UserStatus
from app.domain.value_objects import Email
from app.security.constants import TOKEN_TYPE_BEARER
from app.security.exceptions import AuthenticationError
from app.security.jwt import JWTHelper
from app.security.password import PasswordHasher

if TYPE_CHECKING:
    from app.services.auth.session_service import SessionService


class AuthenticationService:
    """Service orchestrating user login authentication and logout.

    Attributes:
        _uow: Unit of Work for accessing repositories.
        _password_hasher: Argon2 password hashing utility.
        _jwt_helper: JWT encoding and decoding utility.
        _settings: Active application settings.
        _session_service: SessionService instance for managing session state.
    """

    def __init__(
        self,
        unit_of_work: UnitOfWork,
        password_hasher: PasswordHasher | None = None,
        jwt_helper: JWTHelper | None = None,
        settings: ApplicationSettings | None = None,
        session_service: SessionService | None = None,
    ) -> None:
        """Initialize the authentication service.

        Args:
            unit_of_work: Unit of Work for repository access.
            password_hasher: PasswordHasher instance.
            jwt_helper: JWTHelper instance.
            settings: Optional ApplicationSettings instance.
            session_service: Optional SessionService instance.
        """
        self._uow = unit_of_work
        self._password_hasher = password_hasher or PasswordHasher()
        self._jwt_helper = jwt_helper or JWTHelper(settings)
        self._settings = settings or get_settings()
        self._session_service = session_service

    async def authenticate_user(
        self,
        email: str,
        password: str,
        user_agent: str = "",
        ip_address: str = "",
    ) -> dict[str, Any]:
        """Authenticate a user by email and password.

        Args:
            email: Plaintext email address string.
            password: Plaintext account password string.
            user_agent: Client User-Agent string.
            ip_address: Client IP address string.

        Returns:
            Dict containing access_token, refresh_token, token_type, expires_in,
            and user info details.

        Raises:
            AuthenticationError: When user is not found, disabled, or password mismatch.
        """
        generic_error = "Invalid email or password"

        try:
            email_vo = Email(email.strip())
        except Exception as err:
            raise AuthenticationError(generic_error) from err

        async with self._uow as uow:
            user = await uow.users.find_by_email(email_vo)

        if user is None:
            raise AuthenticationError(generic_error)

        if user.status in (UserStatus.DELETED, UserStatus.DISABLED):
            raise AuthenticationError(generic_error)

        stored_hash = user.metadata.value.get(
            "hashed_password"
        ) or user.metadata.value.get("password_hash")
        if not stored_hash or not isinstance(stored_hash, str):
            raise AuthenticationError(generic_error)

        if not self._password_hasher.verify_password(password, stored_hash):
            raise AuthenticationError(generic_error)

        claims = {
            "sub": str(user.user_id.value),
            "email": str(user.email.value),
            "role": user.role.value,
        }

        access_token = self._jwt_helper.create_access_token(data=claims)
        expire_minutes = self._settings.access_token_expire_minutes or 30
        expires_in_seconds = expire_minutes * 60

        raw_refresh_token: str | None = None
        if self._session_service is not None:
            _, raw_refresh_token = await self._session_service.create_session(
                user_id=str(user.user_id.value),
                user_agent=user_agent,
                ip_address=ip_address,
            )

        return {
            "access_token": access_token,
            "refresh_token": raw_refresh_token,
            "token_type": TOKEN_TYPE_BEARER,
            "expires_in": expires_in_seconds,
            "user": {
                "id": str(user.user_id.value),
                "email": str(user.email.value),
                "display_name": str(user.display_name.value),
                "role": user.role.value,
                "status": user.status.value,
            },
        }

    async def logout_user(self, refresh_token: str | None = None) -> bool:
        """Perform user logout and invalidate active session.

        Args:
            refresh_token: Optional plaintext refresh token string.

        Returns:
            True upon successful logout acknowledgment.
        """
        if self._session_service is not None and refresh_token:
            await self._session_service.invalidate_session_by_token(refresh_token)
        return True
