"""API Key domain entity and status enumeration.

Defines the :class:`ApiKeyStatus` enum and :class:`ApiKey` domain aggregate entity.
"""

from __future__ import annotations

import uuid
from enum import StrEnum

from app.domain.aggregate import AggregateRoot
from app.domain.api_keys.events import ApiKeyCreated, ApiKeyRevoked
from app.domain.api_keys.exceptions import (
    ApiKeyExpiredError,
    ApiKeyRevokedError,
)
from app.domain.entity import Identity
from app.domain.value_objects import Timestamp, UuidIdentity


class ApiKeyStatus(StrEnum):
    """Status states of an API Key.

    Members:
        ACTIVE: The key is active and valid for authentication.
        REVOKED: The key has been revoked and can no longer be used.
        EXPIRED: The key has passed its expiration timestamp.
    """

    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class ApiKey(AggregateRoot[uuid.UUID]):
    """API Key aggregate entity representing workspace-scoped access credentials.

    Attributes:
        workspace_id: UUID identity of the owning workspace.
        name: Human-readable name for the key.
        prefix: Public prefix string (e.g. 'twib_live_a1b2c3d4').
        hashed_secret: SHA-256 hash digest of the secret part.
        permissions: Set of granted permission strings.
        created_at: Timestamp when key was created.
        expires_at: Optional timestamp when key expires.
        last_used_at: Optional timestamp of last activity.
        status: Current status state.
    """

    def __init__(
        self,
        api_key_id: UuidIdentity,
        workspace_id: UuidIdentity,
        name: str,
        prefix: str,
        hashed_secret: str,
        permissions: set[str] | None = None,
        created_at: Timestamp | None = None,
        expires_at: Timestamp | None = None,
        last_used_at: Timestamp | None = None,
        status: ApiKeyStatus = ApiKeyStatus.ACTIVE,
    ) -> None:
        """Initialize an API Key entity.

        Args:
            api_key_id: Unique UUID identity for the key.
            workspace_id: Owning workspace UUID identity.
            name: Human-readable display name.
            prefix: Key prefix string.
            hashed_secret: SHA-256 hash digest of the secret string.
            permissions: Optional set of permission strings.
            created_at: Creation timestamp (defaults to current UTC time).
            expires_at: Optional expiration timestamp.
            last_used_at: Optional timestamp of last usage.
            status: Initial status state (defaults to ACTIVE).
        """
        super().__init__(Identity(api_key_id.value))
        self._api_key_id = api_key_id
        self._workspace_id = workspace_id
        self._name = name
        self._prefix = prefix
        self._hashed_secret = hashed_secret
        self._permissions: set[str] = set(permissions) if permissions else set()
        self._created_at = created_at or Timestamp.now()
        self._expires_at = expires_at
        self._last_used_at = last_used_at
        self._status = status

    @property
    def api_key_id(self) -> UuidIdentity:
        """Return the UUID identity of the API key."""
        return self._api_key_id

    @property
    def workspace_id(self) -> UuidIdentity:
        """Return the workspace UUID identity."""
        return self._workspace_id

    @property
    def name(self) -> str:
        """Return human-readable display name."""
        return self._name

    @property
    def prefix(self) -> str:
        """Return public prefix string."""
        return self._prefix

    @property
    def hashed_secret(self) -> str:
        """Return SHA-256 hash digest of secret."""
        return self._hashed_secret

    @property
    def permissions(self) -> set[str]:
        """Return set of granted permission strings."""
        return set(self._permissions)

    @property
    def created_at(self) -> Timestamp:
        """Return creation timestamp."""
        return self._created_at

    @property
    def expires_at(self) -> Timestamp | None:
        """Return optional expiration timestamp."""
        return self._expires_at

    @property
    def last_used_at(self) -> Timestamp | None:
        """Return optional last activity timestamp."""
        return self._last_used_at

    @property
    def status(self) -> ApiKeyStatus:
        """Return current status state."""
        return self._status

    def is_active(self) -> bool:
        """Check if the key is active and not expired.

        Returns:
            True if status is ACTIVE and not expired, False otherwise.
        """
        if self._status is not ApiKeyStatus.ACTIVE:
            return False
        return not self.is_expired()

    def is_expired(self) -> bool:
        """Check if the key has passed its expiration time.

        Returns:
            True if current time >= expires_at, False otherwise.
        """
        if self._expires_at is None:
            return False
        return Timestamp.now().value >= self._expires_at.value

    def validate_usable(self) -> None:
        """Validate that the key is active and not expired or revoked.

        Raises:
            ApiKeyRevokedError: If the key has been revoked.
            ApiKeyExpiredError: If the key has expired.
        """
        if self._status is ApiKeyStatus.REVOKED:
            raise ApiKeyRevokedError(f"API key '{self._prefix}' has been revoked.")
        if self.is_expired() or self._status is ApiKeyStatus.EXPIRED:
            raise ApiKeyExpiredError(f"API key '{self._prefix}' has expired.")

    def revoke(self) -> None:
        """Revoke the API key."""
        if self._status is ApiKeyStatus.REVOKED:
            return
        self._status = ApiKeyStatus.REVOKED
        revoked_at = Timestamp.now()
        self.record_event(
            ApiKeyRevoked(
                api_key_id=self._api_key_id,
                workspace_id=self._workspace_id,
                revoked_at=revoked_at,
            )
        )

    def mark_used(self) -> None:
        """Record activity timestamp when the key is successfully used."""
        self._last_used_at = Timestamp.now()

    @classmethod
    def create(
        cls,
        api_key_id: UuidIdentity,
        workspace_id: UuidIdentity,
        name: str,
        prefix: str,
        hashed_secret: str,
        permissions: set[str] | None = None,
        expires_at: Timestamp | None = None,
    ) -> ApiKey:
        """Factory method creating a new active ApiKey entity and raising event.

        Args:
            api_key_id: Unique UUID identity.
            workspace_id: Owning workspace UUID identity.
            name: Display name.
            prefix: Key prefix identifier.
            hashed_secret: SHA-256 hashed secret.
            permissions: Optional scope permissions.
            expires_at: Optional expiration timestamp.

        Returns:
            A new ApiKey instance with recorded ApiKeyCreated domain event.
        """
        created_at = Timestamp.now()
        key = ApiKey(
            api_key_id=api_key_id,
            workspace_id=workspace_id,
            name=name,
            prefix=prefix,
            hashed_secret=hashed_secret,
            permissions=permissions,
            created_at=created_at,
            expires_at=expires_at,
            status=ApiKeyStatus.ACTIVE,
        )
        key.record_event(
            ApiKeyCreated(
                api_key_id=api_key_id,
                workspace_id=workspace_id,
                name=name,
                prefix=prefix,
                created_at=created_at,
            )
        )
        return key
