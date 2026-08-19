"""Authentication application service.

Handles user login authentication, user registration, password verification
against stored hashes, JWT access token issuance, and logout handling.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

import structlog

from app.core.config import get_settings
from app.core.settings import ApplicationSettings
from app.domain.exceptions import BusinessRuleViolation
from app.domain.repositories.unit_of_work import UnitOfWork
from app.domain.users.exceptions import EmailAlreadyAssigned
from app.domain.users.role import UserRole
from app.domain.users.status import UserStatus
from app.domain.users.user import User
from app.domain.value_objects import Email, Metadata, Name, UuidIdentity
from app.security.constants import TOKEN_TYPE_BEARER
from app.security.exceptions import AuthenticationError
from app.security.jwt import JWTHelper
from app.security.password import PasswordHasher

if TYPE_CHECKING:
    from app.services.auth.session_service import SessionService

logger = structlog.get_logger(__name__)


class AuthenticationService:
    """Service orchestrating user registration, authentication, and logout.

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
        """Initialize the AuthenticationService.

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

    async def register_user(
        self,
        email: str,
        password: str,
        display_name: str | None = None,
        user_agent: str = "",
        ip_address: str = "",
    ) -> dict[str, Any]:
        """Register a new user, store hashed credentials, and issue tokens.

        Args:
            email: Plaintext email address string.
            password: Plaintext account password string.
            display_name: Optional display name for the user.
            user_agent: Client User-Agent string.
            ip_address: Client IP address string.

        Returns:
            Dict containing access_token, refresh_token, token_type, expires_in,
            and user info details.

        Raises:
            EmailAlreadyAssigned: When email address is already registered.
            BusinessRuleViolation: When a domain rule is violated.
        """
        try:
            email_vo = Email(email.strip())
        except Exception as err:
            raise BusinessRuleViolation(f"Invalid email format: '{email}'") from err

        async with self._uow as uow:
            existing_user = await uow.users.find_by_email(email_vo)
            if existing_user is not None:
                raise EmailAlreadyAssigned(f"Email '{email}' is already registered")

            resolved_name = (display_name or "").strip()
            if not resolved_name:
                resolved_name = email.split("@")[0]
            name_vo = Name(resolved_name)

            hashed_password = self._password_hasher.hash_password(password)

            user_id = UuidIdentity(uuid.uuid4())
            user = User(
                user_id=user_id,
                email=email_vo,
                display_name=name_vo,
                status=UserStatus.ACTIVE,
                role=UserRole.MEMBER,
                metadata=Metadata({"hashed_password": hashed_password}),
            )

            await uow.users.save(user)
            await uow.commit()

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
            try:
                _, raw_refresh_token = await self._session_service.create_session(
                    user_id=str(user.user_id.value),
                    user_agent=user_agent,
                    ip_address=ip_address,
                )
            except Exception as session_err:
                logger.warning(
                    "Redis session creation bypassed during registration",
                    error=str(session_err),
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
            try:
                _, raw_refresh_token = await self._session_service.create_session(
                    user_id=str(user.user_id.value),
                    user_agent=user_agent,
                    ip_address=ip_address,
                )
            except Exception as session_err:
                logger.warning(
                    "Redis session creation bypassed during authentication",
                    error=str(session_err),
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
            try:
                await self._session_service.invalidate_session_by_token(refresh_token)
            except Exception as session_err:
                logger.warning(
                    "Redis session invalidation error",
                    error=str(session_err),
                )
        return True
