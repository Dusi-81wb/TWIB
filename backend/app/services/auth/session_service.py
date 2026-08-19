"""Redis-backed session management and refresh token service.

Handles active session storage, refresh token issuance, secure token rotation,
single-device logout, and all-device session invalidation using Redis.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import get_settings
from app.core.settings import ApplicationSettings
from app.domain.repositories.unit_of_work import UnitOfWork
from app.domain.users.status import UserStatus
from app.domain.value_objects import UuidIdentity
from app.infrastructure.cache import RedisClient
from app.security.constants import TOKEN_TYPE_BEARER
from app.security.exceptions import InvalidTokenError
from app.security.jwt import JWTHelper
from app.security.refresh_token import generate_refresh_token, hash_refresh_token
from app.security.session import SessionData

DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7


class SessionService:
    """Service managing user sessions and refresh tokens in Redis.

    Attributes:
        _redis: RedisClient wrapper instance.
        _uow: UnitOfWork for database validation.
        _jwt_helper: JWTHelper for access token minting.
        _settings: Active ApplicationSettings.
    """

    def __init__(
        self,
        redis_client: RedisClient,
        unit_of_work: UnitOfWork,
        jwt_helper: JWTHelper | None = None,
        settings: ApplicationSettings | None = None,
    ) -> None:
        """Initialize the session service.

        Args:
            redis_client: Redis client wrapper.
            unit_of_work: Unit of Work for database verification.
            jwt_helper: Optional JWTHelper instance.
            settings: Optional ApplicationSettings instance.
        """
        self._redis = redis_client
        self._uow = unit_of_work
        self._settings = settings or get_settings()
        self._jwt_helper = jwt_helper or JWTHelper(self._settings)

    async def create_session(
        self,
        user_id: str,
        user_agent: str = "",
        ip_address: str = "",
    ) -> tuple[SessionData, str]:
        """Create and store a new active session in Redis.

        Args:
            user_id: User UUID string.
            user_agent: Client User-Agent string.
            ip_address: Client IP address string.

        Returns:
            Tuple of (SessionData, raw_refresh_token).
        """
        raw_refresh_token, refresh_hash = generate_refresh_token()
        session_id = str(uuid.uuid4())

        now_dt = datetime.now(UTC)
        ttl_seconds = DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS * 86400
        expires_dt = now_dt + timedelta(days=DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS)

        session = SessionData(
            session_id=session_id,
            user_id=user_id,
            refresh_token_hash=refresh_hash,
            issued_at=now_dt.isoformat(),
            expires_at=expires_dt.isoformat(),
            last_activity=now_dt.isoformat(),
            user_agent=user_agent,
            ip_address=ip_address,
        )

        session_key = f"session:{session_id}"
        hash_key = f"refresh_hash:{refresh_hash}"

        await self._redis.set(
            session_key, session.to_json(), expire_seconds=ttl_seconds
        )
        await self._redis.set(hash_key, session_id, expire_seconds=ttl_seconds)

        return session, raw_refresh_token

    async def refresh_tokens(
        self,
        raw_refresh_token: str,
    ) -> dict[str, Any]:
        """Rotate a refresh token and issue a new JWT access token.

        Args:
            raw_refresh_token: Incoming plaintext refresh token string.

        Returns:
            Dict containing access_token, refresh_token, token_type, and expires_in.

        Raises:
            InvalidTokenError: When refresh token is invalid or user inactive.
        """
        if not raw_refresh_token:
            raise InvalidTokenError("Refresh token is required")

        old_hash = hash_refresh_token(raw_refresh_token)
        hash_key = f"refresh_hash:{old_hash}"
        session_id = await self._redis.get(hash_key)

        if not session_id:
            raise InvalidTokenError("Invalid or expired refresh token")

        session_key = f"session:{session_id}"
        session_json = await self._redis.get(session_key)

        if not session_json:
            await self._redis.delete(hash_key)
            raise InvalidTokenError("Session not found or expired")

        session = SessionData.from_json(session_json)
        if session.is_expired():
            await self._redis.delete(session_key, hash_key)
            raise InvalidTokenError("Session has expired")

        # Validate user account status in database
        try:
            user_uuid = uuid.UUID(session.user_id)
        except ValueError as err:
            raise InvalidTokenError("Invalid user identity in session") from err

        async with self._uow as uow:
            user = await uow.users.find_by_id(UuidIdentity(user_uuid))

        if user is None or user.status in (UserStatus.DELETED, UserStatus.DISABLED):
            await self._redis.delete(session_key, hash_key)
            raise InvalidTokenError("User account is inactive or disabled")

        # ROTATE REFRESH TOKEN: invalidate old hash and store new hash
        await self._redis.delete(hash_key)

        new_raw_refresh, new_hash = generate_refresh_token()
        new_hash_key = f"refresh_hash:{new_hash}"

        now_dt = datetime.now(UTC)
        ttl_seconds = DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS * 86400

        session.refresh_token_hash = new_hash
        session.last_activity = now_dt.isoformat()

        await self._redis.set(
            session_key, session.to_json(), expire_seconds=ttl_seconds
        )
        await self._redis.set(new_hash_key, session_id, expire_seconds=ttl_seconds)

        # Issue new JWT access token
        claims = {
            "sub": str(user.user_id.value),
            "email": str(user.email.value),
            "role": user.role.value,
        }
        new_access_token = self._jwt_helper.create_access_token(data=claims)
        expire_minutes = self._settings.access_token_expire_minutes or 30

        return {
            "access_token": new_access_token,
            "refresh_token": new_raw_refresh,
            "token_type": TOKEN_TYPE_BEARER,
            "expires_in": expire_minutes * 60,
        }

    async def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a specific session by session ID.

        Args:
            session_id: Target session UUID string.

        Returns:
            True if session was removed or nonexistent.
        """
        session_key = f"session:{session_id}"
        session_json = await self._redis.get(session_key)

        if session_json:
            try:
                session = SessionData.from_json(session_json)
                hash_key = f"refresh_hash:{session.refresh_token_hash}"
                await self._redis.delete(session_key, hash_key)
            except Exception:
                await self._redis.delete(session_key)
        return True

    async def invalidate_session_by_token(self, raw_refresh_token: str) -> bool:
        """Invalidate a session associated with a raw refresh token.

        Args:
            raw_refresh_token: Plaintext refresh token string.

        Returns:
            True upon completion.
        """
        if not raw_refresh_token:
            return True

        old_hash = hash_refresh_token(raw_refresh_token)
        hash_key = f"refresh_hash:{old_hash}"
        session_id = await self._redis.get(hash_key)

        if session_id:
            await self.invalidate_session(session_id)
        else:
            await self._redis.delete(hash_key)
        return True

    async def invalidate_all_user_sessions(self, user_id: str) -> int:
        """Invalidate all active sessions for a specific user ID.

        Args:
            user_id: User UUID string.

        Returns:
            Count of sessions invalidated.
        """
        if not user_id:
            return 0

        keys = await self._redis.keys("session:*")
        count = 0
        for session_key in keys:
            session_json = await self._redis.get(session_key)
            if not session_json:
                continue

            try:
                session = SessionData.from_json(session_json)
            except Exception:
                await self._redis.delete(session_key)
                continue

            if session.user_id == user_id:
                hash_key = f"refresh_hash:{session.refresh_token_hash}"
                await self._redis.delete(session_key, hash_key)
                count += 1

        return count
