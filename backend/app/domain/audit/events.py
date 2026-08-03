"""Audit Log domain events.

Defines immutable domain events raised when audit log entries are recorded.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.event import DomainEvent
from app.domain.value_objects import Timestamp, UuidIdentity


@dataclass(frozen=True)
class AuditLogRecorded(DomainEvent):
    """Domain event raised when a security audit log entry is recorded.

    Attributes:
        audit_log_id: UUID identity of the audit log entry.
        action: Audited action string (e.g. 'user.login').
        user_id: Optional UUID identity of the acting user.
        timestamp: Time of the audited event.
    """

    audit_log_id: UuidIdentity
    action: str
    user_id: UuidIdentity | None
    timestamp: Timestamp
