"""User status enumeration.

A :class:`UserStatus` is the immutable, string-valued representation of the
lifecycle state of a :class:`~app.domain.users.user.User` aggregate. Statuses
are domain concepts; the transitions between them are enforced by the user
aggregate's business rules.
"""

from __future__ import annotations

from enum import StrEnum


class UserStatus(StrEnum):
    """The lifecycle states a user can be in.

    Members:
        PENDING: The user was created but has not been activated yet.
        ACTIVE: The user can use the platform.
        SUSPENDED: The user was temporarily suspended.
        DISABLED: The user was deactivated and cannot sign in.
        DELETED: The user was deleted; this state is terminal.
    """

    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DISABLED = "disabled"
    DELETED = "deleted"
