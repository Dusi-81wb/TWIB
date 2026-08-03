"""Audit Log domain package.

Provides domain aggregate entity, action constants, and events:
- :class:`~app.domain.audit.audit_log.AuditLog`: Audit log entity.
- :class:`~app.domain.audit.events.AuditLogRecorded`: Event recorded.
- Action constants (:data:`~app.domain.audit.audit_log.ACTION_USER_LOGIN`, etc.).
"""

from app.domain.audit.audit_log import (
    ACTION_API_KEY_CREATED,
    ACTION_API_KEY_DELETED,
    ACTION_ORGANIZATION_CREATED,
    ACTION_PERMISSION_CHANGED,
    ACTION_ROLE_CHANGED,
    ACTION_USER_LOGIN,
    ACTION_USER_LOGOUT,
    ACTION_WORKSPACE_CREATED,
    AuditLog,
    sanitize_metadata,
)
from app.domain.audit.events import AuditLogRecorded

__all__ = [
    "ACTION_API_KEY_CREATED",
    "ACTION_API_KEY_DELETED",
    "ACTION_ORGANIZATION_CREATED",
    "ACTION_PERMISSION_CHANGED",
    "ACTION_ROLE_CHANGED",
    "ACTION_USER_LOGIN",
    "ACTION_USER_LOGOUT",
    "ACTION_WORKSPACE_CREATED",
    "AuditLog",
    "AuditLogRecorded",
    "sanitize_metadata",
]
