"""JSON Web Token (JWT) creation and validation utilities.

Provides helper utilities to mint and decode access tokens using PyJWT.
Security credentials and algorithm defaults are loaded from application settings.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from app.core.config import get_settings
from app.core.settings import ApplicationSettings
from app.security.constants import (
    DEFAULT_JWT_ALGORITHM,
    TOKEN_TYPE_ACCESS,
)
from app.security.exceptions import InvalidTokenError, TokenExpiredError


class JWTHelper:
    """Reusable utility for JWT access token encoding and decoding."""

    def __init__(self, settings: ApplicationSettings | None = None) -> None:
        """Initialize the JWT helper bound to settings.

        Args:
            settings: Optional application settings.
        """
        self._settings = settings

    def _resolve_secret_key(self, secret_key: str | None = None) -> str:
        """Resolve the active secret key.

        Args:
            secret_key: Optional explicit secret key.

        Returns:
            The resolved secret key string.

        Raises:
            InvalidTokenError: If no secret key is configured.
        """
        if secret_key:
            return secret_key

        cfg = self._settings or get_settings()
        key = cfg.jwt_secret_key or cfg.secret_key
        if not key:
            # Fallback for development if secret key is blank
            key = "twib-development-secret-key-change-in-production"
        return key

    def _resolve_algorithm(self, algorithm: str | None = None) -> str:
        """Resolve the active signing algorithm.

        Args:
            algorithm: Optional explicit algorithm.

        Returns:
            The resolved algorithm string.
        """
        if algorithm:
            return algorithm
        cfg = self._settings or get_settings()
        return cfg.jwt_algorithm or DEFAULT_JWT_ALGORITHM

    def create_access_token(
        self,
        data: dict[str, Any],
        secret_key: str | None = None,
        expires_delta: timedelta | int | None = None,
        algorithm: str | None = None,
    ) -> str:
        """Create a signed JWT access token.

        Args:
            data: Subject and claim payload dictionary.
            secret_key: Optional explicit secret key override.
            expires_delta: Token lifetime as timedelta or seconds integer.
            algorithm: Optional signing algorithm override.

        Returns:
            The encoded JWT token string.
        """
        to_encode = data.copy()
        key = self._resolve_secret_key(secret_key)
        algo = self._resolve_algorithm(algorithm)

        now = datetime.now(UTC)
        if isinstance(expires_delta, timedelta):
            expire = now + expires_delta
        elif isinstance(expires_delta, int):
            expire = now + timedelta(seconds=expires_delta)
        else:
            cfg = self._settings or get_settings()
            expire_minutes = cfg.access_token_expire_minutes or 30
            expire = now + timedelta(minutes=expire_minutes)

        to_encode.update(
            {
                "exp": expire,
                "iat": now,
                "type": TOKEN_TYPE_ACCESS,
            }
        )

        return jwt.encode(to_encode, key, algorithm=algo)

    def decode_token(
        self,
        token: str,
        secret_key: str | None = None,
        algorithm: str | None = None,
        verify_exp: bool = True,
    ) -> dict[str, Any]:
        """Decode and validate a JWT access token payload.

        Args:
            token: The raw JWT token string.
            secret_key: Optional explicit secret key override.
            algorithm: Optional algorithm override.
            verify_exp: Whether to verify token expiration.

        Returns:
            The decoded payload dictionary.

        Raises:
            TokenExpiredError: If the token has expired.
            InvalidTokenError: If the token is invalid or signature check fails.
        """
        key = self._resolve_secret_key(secret_key)
        algo = self._resolve_algorithm(algorithm)

        options: dict[str, Any] = {"verify_exp": verify_exp}

        try:
            payload: dict[str, Any] = jwt.decode(
                token,
                key,
                algorithms=[algo],
                options=options,  # type: ignore[arg-type]
            )
            return payload
        except jwt.ExpiredSignatureError as err:
            raise TokenExpiredError("JWT token has expired") from err
        except jwt.PyJWTError as err:
            raise InvalidTokenError(f"Invalid JWT token: {err}") from err


_default_jwt_helper = JWTHelper()


def create_access_token(
    data: dict[str, Any],
    secret_key: str | None = None,
    expires_delta: timedelta | int | None = None,
    algorithm: str | None = None,
) -> str:
    """Create a signed JWT access token using the default JWTHelper."""
    return _default_jwt_helper.create_access_token(
        data=data,
        secret_key=secret_key,
        expires_delta=expires_delta,
        algorithm=algorithm,
    )


def decode_token(
    token: str,
    secret_key: str | None = None,
    algorithm: str | None = None,
    verify_exp: bool = True,
) -> dict[str, Any]:
    """Decode and validate a JWT access token using the default JWTHelper."""
    return _default_jwt_helper.decode_token(
        token=token,
        secret_key=secret_key,
        algorithm=algorithm,
        verify_exp=verify_exp,
    )
