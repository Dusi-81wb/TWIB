"""Audit Log domain aggregate entity and security action constants.

Defines the :class:`AuditLog` domain aggregate entity and standard action
string constants.
"""

from __future__ import annotations

import uuid
from typing import Any

from app.domain.aggregate import AggregateRoot
from app.domain.audit.events import AuditLogRecorded
from app.domain.entity import Identity
from app.domain.value_objects import Timestamp, UuidIdentity

# Standard Audited Actions
ACTION_USER_LOGIN: str = "user.login"
ACTION_USER_LOGOUT: str = "user.logout"
ACTION_API_KEY_CREATED: str = "api_key.created"
ACTION_API_KEY_DELETED: str = "api_key.deleted"
ACTION_WORKSPACE_CREATED: str = "workspace.created"
ACTION_ORGANIZATION_CREATED: str = "organization.created"
ACTION_ROLE_CHANGED: str = "role.changed"
ACTION_PERMISSION_CHANGED: str = "permission.changed"

SENSITIVE_KEYS: set[str] = {
    "password",
    "secret",
    "api_key",
    "token",
    "access_token",
    "refresh_token",
    "authorization",
    "credentials",
}


def sanitize_metadata(data: dict[str, Any] | None) -> dict[str, Any]:
    """Sanitize metadata dictionary by redacting sensitive keys.

    Args:
        data: Input metadata dictionary.

    Returns:
        Sanitized metadata dictionary with sensitive fields redacted.
    """
    if not data:
        return {}

    sanitized: dict[str, Any] = {}
    for key, val in data.items():
        if key.lower() in SENSITIVE_KEYS:
            sanitized[key] = "[REDACTED]"
        elif isinstance(val, dict):
            sanitized[key] = sanitize_metadata(val)
        else:
            sanitized[key] = val

    return sanitized


class AuditLog(AggregateRoot[uuid.UUID]):
    """Audit Log aggregate entity recording security-sensitive operations.

    Attributes:
        organization_id: Optional UUID of the organization context.
        workspace_id: Optional UUID of the workspace context.
        user_id: Optional UUID of the actor user.
        action: Audited action identifier string.
        resource_type: Type of resource affected (e.g. 'user', 'api_key').
        resource_id: Optional identifier string of target resource.
        ip_address: Client IP address string.
        user_agent: Client User-Agent header string.
        timestamp: UTC timestamp when action occurred.
        metadata: Contextual metadata key-value dictionary (sanitized).
    """

    def __init__(
        self,
        audit_log_id: UuidIdentity,
        action: str,
        resource_type: str,
        organization_id: UuidIdentity | None = None,
        workspace_id: UuidIdentity | None = None,
        user_id: UuidIdentity | None = None,
        resource_id: str | None = None,
        ip_address: str = "",
        user_agent: str = "",
        timestamp: Timestamp | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize an AuditLog entity.

        Args:
            audit_log_id: Unique UUID identity for the audit entry.
            action: Action string.
            resource_type: Affected resource type string.
            organization_id: Optional Organization UUID.
            workspace_id: Optional Workspace UUID.
            user_id: Optional actor User UUID.
            resource_id: Optional target resource ID string.
            ip_address: Client IP address.
            user_agent: Client User-Agent string.
            timestamp: Timestamp (defaults to current UTC time).
            metadata: Context metadata dictionary (auto-sanitized).
        """
        super().__init__(Identity(audit_log_id.value))
        self._organization_id = organization_id
        self._workspace_id = workspace_id
        self._user_id = user_id
        self._action = action
        self._resource_type = resource_type
        self._resource_id = resource_id
        self._ip_address = ip_address
        self._user_agent = user_agent
        self._timestamp = timestamp or Timestamp.now()
        self._metadata = sanitize_metadata(metadata)

    @property
    def organization_id(self) -> UuidIdentity | None:
        """Return organization UUID, if set."""
        return self._organization_id

    @property
    def workspace_id(self) -> UuidIdentity | None:
        """Return workspace UUID, if set."""
        return self._workspace_id

    @property
    def user_id(self) -> UuidIdentity | None:
        """Return actor user UUID, if set."""
        return self._user_id

    @property
    def action(self) -> str:
        """Return audited action string."""
        return self._action

    @property
    def resource_type(self) -> str:
        """Return affected resource type."""
        return self._resource_type

    @property
    def resource_id(self) -> str | None:
        """Return target resource ID, if set."""
        return self._resource_id

    @property
    def ip_address(self) -> str:
        """Return client IP address."""
        return self._ip_address

    @property
    def user_agent(self) -> str:
        """Return client User-Agent string."""
        return self._user_agent

    @property
    def timestamp(self) -> Timestamp:
        """Return timestamp of the audited operation."""
        return self._timestamp

    @property
    def metadata(self) -> dict[str, Any]:
        """Return sanitized metadata dictionary."""
        return dict(self._metadata)

    @classmethod
    def create(
        cls,
        audit_log_id: UuidIdentity,
        action: str,
        resource_type: str,
        organization_id: UuidIdentity | None = None,
        workspace_id: UuidIdentity | None = None,
        user_id: UuidIdentity | None = None,
        resource_id: str | None = None,
        ip_address: str = "",
        user_agent: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> AuditLog:
        """Factory method creating an AuditLog entity and recording domain event.

        Args:
            audit_log_id: Unique UUID identity.
            action: Action string.
            resource_type: Affected resource type.
            organization_id: Optional Organization UUID.
            workspace_id: Optional Workspace UUID.
            user_id: Optional actor User UUID.
            resource_id: Optional resource ID string.
            ip_address: Client IP.
            user_agent: Client User-Agent.
            metadata: Context metadata.

        Returns:
            A new AuditLog instance with recorded AuditLogRecorded domain event.
        """
        ts = Timestamp.now()
        log = AuditLog(
            audit_log_id=audit_log_id,
            action=action,
            resource_type=resource_type,
            organization_id=organization_id,
            workspace_id=workspace_id,
            user_id=user_id,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=ts,
            metadata=metadata,
        )
        log.record_event(
            AuditLogRecorded(
                audit_log_id=audit_log_id,
                action=action,
                user_id=user_id,
                timestamp=ts,
            )
        )
        return log
