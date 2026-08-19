"""User domain package.

This package models the user aggregate, the core business entity of TWIB. It
contains the :class:`~app.domain.users.user.User` aggregate root, the
:class:`~app.domain.users.status.UserStatus` and
:class:`~app.domain.users.role.UserRole` domain enums, the user domain events,
and the user business-rule exceptions.

Everything here is pure Python (standard library only) and depends on the
Phase 2.1 domain foundation and the Phase 2.2 value objects. It contains no
authentication, password, database, or API code.
"""

from __future__ import annotations

from app.domain.users.events import (
    UserActivated,
    UserCreated,
    UserDeleted,
    UserEmailChanged,
    UserNameChanged,
    UserSuspended,
)
from app.domain.users.exceptions import (
    CannotSuspendOwner,
    EmailAlreadyAssigned,
    InvalidUserState,
    UserAlreadyActive,
)
from app.domain.users.role import UserRole
from app.domain.users.status import UserStatus
from app.domain.users.user import User

__all__ = [
    "CannotSuspendOwner",
    "EmailAlreadyAssigned",
    "InvalidUserState",
    "User",
    "UserActivated",
    "UserAlreadyActive",
    "UserCreated",
    "UserDeleted",
    "UserEmailChanged",
    "UserNameChanged",
    "UserRole",
    "UserStatus",
    "UserSuspended",
]
