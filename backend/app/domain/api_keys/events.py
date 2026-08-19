"""API Key domain events.

Defines immutable domain events emitted during the API key lifecycle.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.event import DomainEvent
from app.domain.value_objects import Timestamp, UuidIdentity


@dataclass(frozen=True)
class ApiKeyCreated(DomainEvent):
    """Domain event raised when a new API key is created.

    Attributes:
        api_key_id: UUID identity of the created API key.
        workspace_id: UUID identity of the owning workspace.
        name: Name assigned to the API key.
        prefix: Key prefix identifier.
        created_at: Creation timestamp.
    """

    api_key_id: UuidIdentity
    workspace_id: UuidIdentity
    name: str
    prefix: str
    created_at: Timestamp


@dataclass(frozen=True)
class ApiKeyRevoked(DomainEvent):
    """Domain event raised when an API key is revoked.

    Attributes:
        api_key_id: UUID identity of the revoked API key.
        workspace_id: UUID identity of the owning workspace.
        revoked_at: Timestamp of revocation.
    """

    api_key_id: UuidIdentity
    workspace_id: UuidIdentity
    revoked_at: Timestamp
