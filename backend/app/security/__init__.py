"""Authentication and security foundation package.

Provides password hashing, JWT creation and validation, constants, and custom
security exceptions:

- :class:`~app.security.password.PasswordHasher`: Argon2 password hashing.
- :class:`~app.security.jwt.JWTHelper`: JWT token encoding/decoding helper.
- :func:`~app.security.jwt.create_access_token`: Helper function to encode JWT.
- :func:`~app.security.jwt.decode_token`: Helper function to decode JWT.
"""

from app.security.constants import (
    DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
    DEFAULT_JWT_ALGORITHM,
    HEADER_AUTHORIZATION,
    HEADER_PREFIX_BEARER,
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_BEARER,
)
from app.security.exceptions import (
    AuthenticationError,
    InvalidPasswordError,
    InvalidTokenError,
    SecurityError,
    TokenExpiredError,
)
from app.security.jwt import JWTHelper, create_access_token, decode_token
from app.security.password import PasswordHasher
from app.security.refresh_token import (
    generate_refresh_token,
    hash_refresh_token,
    verify_refresh_token_hash,
)
from app.security.session import SessionData

__all__ = [
    "DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES",
    "DEFAULT_JWT_ALGORITHM",
    "HEADER_AUTHORIZATION",
    "HEADER_PREFIX_BEARER",
    "TOKEN_TYPE_ACCESS",
    "TOKEN_TYPE_BEARER",
    "AuthenticationError",
    "InvalidPasswordError",
    "InvalidTokenError",
    "JWTHelper",
    "PasswordHasher",
    "SecurityError",
    "SessionData",
    "TokenExpiredError",
    "create_access_token",
    "decode_token",
    "generate_refresh_token",
    "hash_refresh_token",
    "verify_refresh_token_hash",
]
