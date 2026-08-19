"""Audit Service for recording and querying security audit logs.

Provides methods for recording security-sensitive operations and retrieving
filtered, paginated audit records.
"""

from __future__ import annotations

import uuid
from contextlib import suppress
from datetime import datetime
from typing import Any

from app.domain.audit.audit_log import AuditLog
from app.domain.value_objects import UuidIdentity


class AuditService:
    """Service managing security audit log creation and query filtering."""

    def __init__(self) -> None:
        """Initialize AuditService with in-memory audit log repository."""
        self._logs: list[AuditLog] = []

    async def record(
        self,
        action: str,
        resource_type: str,
        organization_id: str | None = None,
        workspace_id: str | None = None,
        user_id: str | None = None,
        resource_id: str | None = None,
        ip_address: str = "",
        user_agent: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> AuditLog:
        """Record a new security audit log entry.

        Args:
            action: Action identifier string (e.g. 'user.login').
            resource_type: Affected resource type (e.g. 'user', 'api_key').
            organization_id: Optional Organization UUID string.
            workspace_id: Optional Workspace UUID string.
            user_id: Optional actor User UUID string.
            resource_id: Optional target resource ID string.
            ip_address: Client IP address string.
            user_agent: Client User-Agent string.
            metadata: Context metadata dictionary (auto-sanitized).

        Returns:
            The recorded AuditLog entity.
        """
        o_uuid = UuidIdentity(uuid.UUID(organization_id)) if organization_id else None
        w_uuid = UuidIdentity(uuid.UUID(workspace_id)) if workspace_id else None
        u_uuid = UuidIdentity(uuid.UUID(user_id)) if user_id else None

        log_id = UuidIdentity(uuid.uuid4())
        audit_log = AuditLog.create(
            audit_log_id=log_id,
            action=action,
            resource_type=resource_type,
            organization_id=o_uuid,
            workspace_id=w_uuid,
            user_id=u_uuid,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata,
        )

        self._logs.append(audit_log)
        return audit_log

    async def get_logs(
        self,
        organization_id: str | None = None,
        workspace_id: str | None = None,
        user_id: str | None = None,
        action: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[AuditLog], int]:
        """Query and filter recorded audit logs.

        Args:
            organization_id: Optional filter by Organization UUID.
            workspace_id: Optional filter by Workspace UUID.
            user_id: Optional filter by actor User UUID.
            action: Optional filter by action string.
            start_date: Optional filter by start ISO 8601 UTC timestamp.
            end_date: Optional filter by end ISO 8601 UTC timestamp.
            limit: Maximum number of items to return per page.
            offset: Page offset index.

        Returns:
            Tuple of (list of AuditLog items for page, total matching count).
        """
        filtered: list[AuditLog] = []

        start_dt: datetime | None = None
        end_dt: datetime | None = None
        if start_date:
            with suppress(ValueError):
                start_dt = datetime.fromisoformat(start_date)
        if end_date:
            with suppress(ValueError):
                end_dt = datetime.fromisoformat(end_date)

        for log in self._logs:
            if (
                organization_id
                and log.organization_id
                and str(log.organization_id.value) != organization_id
            ):
                continue
            if (
                workspace_id
                and log.workspace_id
                and str(log.workspace_id.value) != workspace_id
            ):
                continue
            if user_id and log.user_id and str(log.user_id.value) != user_id:
                continue
            if action and log.action.lower() != action.lower():
                continue

            log_dt = log.timestamp.value
            if start_dt and log_dt < start_dt:
                continue
            if end_dt and log_dt > end_dt:
                continue

            filtered.append(log)

        # Sort newest first
        filtered.sort(key=lambda x: x.timestamp.value, reverse=True)

        total = len(filtered)
        paginated = filtered[offset : offset + limit]

        return paginated, total
