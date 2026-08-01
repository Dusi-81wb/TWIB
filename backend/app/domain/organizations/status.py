"""Organization status enumeration.

A :class:`OrganizationStatus` is the immutable, string-valued representation
of the lifecycle state of an organization. The transitions between states are
enforced by the organization aggregate's business rules.
"""

from __future__ import annotations

from enum import StrEnum


class OrganizationStatus(StrEnum):
    """The lifecycle states an organization can be in.

    Members:
        PENDING: The organization was created but has not been activated yet.
        ACTIVE: The organization is active.
        SUSPENDED: The organization was temporarily suspended.
        ARCHIVED: The organization was archived; it cannot be modified until
            restored.
        DELETED: The organization was deleted; this state is terminal.
    """

    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"
    DELETED = "deleted"
