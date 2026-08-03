"""API Key application service.

Handles secure API key generation, SHA-256 secret hashing, key retrieval,
workspace-scoped listing, revocation, and authentication verification.
"""

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from app.domain.api_keys.api_key import ApiKey
from app.domain.api_keys.exceptions import InvalidApiKeyError
from app.domain.value_objects import Timestamp, UuidIdentity

API_KEY_PREFIX_TAG: str = "twib"


class ApiKeyService:
    """Service managing workspace API key lifecycle and authentication."""

    def __init__(self) -> None:
        """Initialize the API key service with in-memory persistence registry."""
        self._keys_by_id: dict[str, ApiKey] = {}
        self._keys_by_prefix: dict[str, ApiKey] = {}

    async def create_api_key(
        self,
        workspace_id: str,
        name: str,
        environment: str = "live",
        expires_in_days: int | None = None,
        permissions: set[str] | None = None,
    ) -> tuple[ApiKey, str]:
        """Generate a new secure API key and persist its hashed secret.

        Args:
            workspace_id: Owning workspace UUID string.
            name: Human-readable name for the key.
            environment: Environment tag ('live' or 'test').
            expires_in_days: Optional lifetime in days.
            permissions: Optional scope permission strings.

        Returns:
            Tuple of (ApiKey entity, full_plaintext_api_key_string).
        """
        try:
            w_uuid = uuid.UUID(workspace_id)
        except ValueError as err:
            raise InvalidApiKeyError("Invalid workspace UUID format") from err

        env_tag = "test" if environment.lower() == "test" else "live"
        prefix_random = secrets.token_hex(4)
        prefix = f"{API_KEY_PREFIX_TAG}_{env_tag}_{prefix_random}"
        secret_part = secrets.token_urlsafe(32)

        raw_api_key = f"{prefix}_{secret_part}"
        hashed_secret = hashlib.sha256(secret_part.encode("utf-8")).hexdigest()

        key_id = UuidIdentity(uuid.uuid4())
        expires_at: Timestamp | None = None
        if expires_in_days and expires_in_days > 0:
            exp_dt = datetime.now(UTC) + timedelta(days=expires_in_days)
            expires_at = Timestamp(exp_dt)

        api_key = ApiKey.create(
            api_key_id=key_id,
            workspace_id=UuidIdentity(w_uuid),
            name=name,
            prefix=prefix,
            hashed_secret=hashed_secret,
            permissions=permissions,
            expires_at=expires_at,
        )

        str_id = str(key_id.value)
        self._keys_by_id[str_id] = api_key
        self._keys_by_prefix[prefix] = api_key

        return api_key, raw_api_key

    async def get_api_key_by_id(self, key_id: str) -> ApiKey | None:
        """Retrieve API key entity by its UUID string.

        Args:
            key_id: Target API key UUID string.

        Returns:
            ApiKey entity if found, None otherwise.
        """
        return self._keys_by_id.get(key_id)

    async def list_api_keys_for_workspace(self, workspace_id: str) -> list[ApiKey]:
        """List all API keys belonging to a specific workspace.

        Args:
            workspace_id: Target workspace UUID string.

        Returns:
            List of ApiKey entities.
        """
        return [
            key
            for key in self._keys_by_id.values()
            if str(key.workspace_id.value) == workspace_id
        ]

    async def revoke_api_key(self, key_id: str) -> ApiKey:
        """Revoke an active API key by ID.

        Args:
            key_id: Target API key UUID string.

        Returns:
            The revoked ApiKey entity.

        Raises:
            InvalidApiKeyError: If API key is not found.
        """
        key = self._keys_by_id.get(key_id)
        if key is None:
            raise InvalidApiKeyError(f"API key with ID '{key_id}' not found.")

        key.revoke()
        return key

    async def verify_api_key(self, raw_api_key: str) -> ApiKey:
        """Verify a plaintext API key and mark usage timestamp.

        Args:
            raw_api_key: Full plaintext API key string.

        Returns:
            The verified ApiKey entity.

        Raises:
            InvalidApiKeyError: If format is invalid or key/secret mismatch.
        """
        if not raw_api_key:
            raise InvalidApiKeyError("API key string is required")

        parts = raw_api_key.split("_")
        if len(parts) < 4 or parts[0] != API_KEY_PREFIX_TAG:
            raise InvalidApiKeyError("Invalid API key format")

        prefix = f"{parts[0]}_{parts[1]}_{parts[2]}"
        secret_part = "_".join(parts[3:])

        key = self._keys_by_prefix.get(prefix)
        if key is None:
            raise InvalidApiKeyError("Invalid API key")

        computed_hash = hashlib.sha256(secret_part.encode("utf-8")).hexdigest()
        if not secrets.compare_digest(computed_hash, key.hashed_secret):
            raise InvalidApiKeyError("Invalid API key")

        key.validate_usable()
        key.mark_used()
        return key
