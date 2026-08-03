"""API Key domain package.

Provides domain aggregate entity, status enum, events, and exceptions:
- :class:`~app.domain.api_keys.api_key.ApiKey`: Domain aggregate entity.
- :class:`~app.domain.api_keys.api_key.ApiKeyStatus`: Status enumeration.
- :class:`~app.domain.api_keys.events.ApiKeyCreated`: Key creation event.
- :class:`~app.domain.api_keys.events.ApiKeyRevoked`: Key revocation event.
- :class:`~app.domain.api_keys.exceptions.InvalidApiKeyError`: Exception.
- :class:`~app.domain.api_keys.exceptions.ApiKeyExpiredError`: Exception.
- :class:`~app.domain.api_keys.exceptions.ApiKeyRevokedError`: Exception.
"""

from app.domain.api_keys.api_key import ApiKey, ApiKeyStatus
from app.domain.api_keys.events import ApiKeyCreated, ApiKeyRevoked
from app.domain.api_keys.exceptions import (
    ApiKeyExpiredError,
    ApiKeyRevokedError,
    InvalidApiKeyError,
)

__all__ = [
    "ApiKey",
    "ApiKeyCreated",
    "ApiKeyExpiredError",
    "ApiKeyRevoked",
    "ApiKeyRevokedError",
    "ApiKeyStatus",
    "InvalidApiKeyError",
]
