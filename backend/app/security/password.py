"""Password hashing and verification utilities.

This module implements :class:`PasswordHasher` using the Argon2 hashing algorithm
via ``pwdlib`` (or ``passlib`` as fallback). Plaintext passwords are never stored
or logged.
"""

from __future__ import annotations

from typing import Any

from app.security.exceptions import InvalidPasswordError

_password_hash: Any = None
_pwd_context: Any = None

try:
    from pwdlib import PasswordHash
    from pwdlib.hashers.argon2 import Argon2Hasher

    _password_hash = PasswordHash((Argon2Hasher(),))
except ImportError:
    try:
        from passlib.context import CryptContext  # type: ignore[import-untyped]

        _pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
        _password_hash = None
    except ImportError:
        _pwd_context = None
        _password_hash = None


class PasswordHasher:
    """Argon2 password hashing and verification component."""

    def hash_password(self, password: str) -> str:
        """Hash a plaintext password using Argon2.

        Args:
            password: The raw plaintext password string.

        Returns:
            The securely hashed password string.

        Raises:
            ValueError: If the password is empty or invalid.
        """
        if not password:
            raise ValueError("Password cannot be empty")

        if _password_hash is not None:
            return str(_password_hash.hash(password))
        if _pwd_context is not None:
            return str(_pwd_context.hash(password))

        raise RuntimeError(
            "No password hashing backend available. "
            "Please install pwdlib[argon2] or passlib[argon2]."
        )

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against an Argon2 hash.

        Args:
            plain_password: The raw plaintext password to check.
            hashed_password: The stored Argon2 password hash.

        Returns:
            True if the password matches the hash, False otherwise.
        """
        if not plain_password or not hashed_password:
            return False

        try:
            if _password_hash is not None:
                return bool(_password_hash.verify(plain_password, hashed_password))
            if _pwd_context is not None:
                return bool(_pwd_context.verify(plain_password, hashed_password))
        except Exception:
            return False

        return False

    def verify_password_or_raise(
        self, plain_password: str, hashed_password: str
    ) -> None:
        """Verify a plaintext password or raise InvalidPasswordError on mismatch.

        Args:
            plain_password: The raw plaintext password to check.
            hashed_password: The stored Argon2 password hash.

        Raises:
            InvalidPasswordError: If the password verification fails.
        """
        if not self.verify_password(plain_password, hashed_password):
            raise InvalidPasswordError("Invalid password provided")
