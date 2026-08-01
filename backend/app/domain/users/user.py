"""User aggregate root.

:class:`User` is the core business entity of TWIB. It is an aggregate root
built from the Phase 2.2 value objects (:class:`UuidIdentity`, :class:`Email`,
:class:`Name`, :class:`Timestamp`, :class:`Metadata`, :class:`Version`) and the
domain enums (:class:`UserStatus`, :class:`UserRole`).

The aggregate exposes its state through read-only properties only, so callers
can never mutate it directly. Every state change happens through a domain
method that validates the operation, records the appropriate domain event, and
bumps the version (optimistic locking).

This module is pure Python: no FastAPI, Pydantic, SQLAlchemy, repository, or
authentication.
"""

from __future__ import annotations

import uuid

from app.domain.aggregate import AggregateRoot
from app.domain.entity import Identity
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
from app.domain.value_objects import (
    Email,
    Metadata,
    Name,
    Timestamp,
    UuidIdentity,
    Version,
)


class User(AggregateRoot[uuid.UUID]):
    """A user of the TWIB platform.

    The user is an aggregate root whose state is entirely built from immutable
    value objects and enums and is exposed through read-only properties. All
    state changes go through domain methods that enforce the user business
    rules, record domain events, and bump the optimistic-locking version.

    Attributes:
        user_id: The stable UUID identity of the user.
        email: The user's email address.
        display_name: The user's display name.
        created_at: When the user was created (UTC).
        updated_at: When the user was last changed (UTC).
        status: The current lifecycle state of the user.
        role: The role the user holds in the organization.
        metadata: The user's key/value metadata map.
        version: The optimistic-locking version of the aggregate.
    """

    _user_id: UuidIdentity
    _email: Email
    _display_name: Name
    _created_at: Timestamp
    _updated_at: Timestamp
    _status: UserStatus
    _role: UserRole
    _metadata: Metadata
    _version: Version

    def __init__(
        self,
        user_id: UuidIdentity,
        email: Email,
        display_name: Name,
        status: UserStatus = UserStatus.PENDING,
        role: UserRole = UserRole.MEMBER,
        created_at: Timestamp | None = None,
        updated_at: Timestamp | None = None,
        metadata: Metadata | None = None,
        version: Version | None = None,
    ) -> None:
        """Initialize a new user aggregate.

        Args:
            user_id: The stable UUID identity of the user.
            email: The user's email address.
            display_name: The user's display name.
            status: The initial lifecycle state (defaults to PENDING).
            role: The role the user holds (defaults to MEMBER).
            created_at: The creation moment (defaults to now, UTC).
            updated_at: The last change moment (defaults to the creation
                moment).
            metadata: The user's metadata map (defaults to empty).
            version: The optimistic-locking version (defaults to 0.0.0).
        """
        super().__init__(Identity(user_id.value))
        now = created_at if created_at is not None else Timestamp.now()
        self._user_id = user_id
        self._email = email
        self._display_name = display_name
        self._status = status
        self._role = role
        self._created_at = now
        self._updated_at = updated_at if updated_at is not None else now
        self._metadata = metadata if metadata is not None else Metadata()
        self._version = version if version is not None else Version(0)
        self.record_event(UserCreated(user_id=self._user_id))

    @property
    def user_id(self) -> UuidIdentity:
        """Return the stable UUID identity of the user."""
        return self._user_id

    @property
    def email(self) -> Email:
        """Return the user's email address."""
        return self._email

    @property
    def display_name(self) -> Name:
        """Return the user's display name."""
        return self._display_name

    @property
    def created_at(self) -> Timestamp:
        """Return when the user was created (UTC)."""
        return self._created_at

    @property
    def updated_at(self) -> Timestamp:
        """Return when the user was last changed (UTC)."""
        return self._updated_at

    @property
    def status(self) -> UserStatus:
        """Return the current lifecycle state of the user."""
        return self._status

    @property
    def role(self) -> UserRole:
        """Return the role the user holds in the organization."""
        return self._role

    @property
    def metadata(self) -> Metadata:
        """Return the user's key/value metadata map."""
        return self._metadata

    @property
    def version(self) -> Version:
        """Return the optimistic-locking version of the aggregate."""
        return self._version

    def change_display_name(self, new_display_name: Name) -> None:
        """Change the user's display name.

        A no-op when the new name equals the current one.

        Args:
            new_display_name: The new display name.

        Raises:
            InvalidUserState: When the user is deleted.
        """
        self._assert_not_deleted()
        if new_display_name == self._display_name:
            return
        previous = self._display_name
        self._display_name = new_display_name
        self._touch()
        self.record_event(
            UserNameChanged(
                user_id=self._user_id,
                display_name=new_display_name,
                previous_display_name=previous,
            )
        )

    def change_email(self, new_email: Email) -> None:
        """Change the user's email address.

        Args:
            new_email: The new email address.

        Raises:
            InvalidUserState: When the user is deleted.
            EmailAlreadyAssigned: When the new email equals the email already
                assigned to this user.
        """
        self._assert_not_deleted()
        if new_email == self._email:
            raise EmailAlreadyAssigned(
                f"Email {new_email} is already assigned to user {self._user_id}"
            )
        previous = self._email
        self._email = new_email
        self._touch()
        self.record_event(
            UserEmailChanged(
                user_id=self._user_id,
                email=new_email,
                previous_email=previous,
            )
        )

    def activate(self) -> None:
        """Activate the user.

        Pending, suspended, and disabled users become active.

        Raises:
            UserAlreadyActive: When the user is already active.
            InvalidUserState: When the user is deleted.
        """
        if self._status is UserStatus.ACTIVE:
            raise UserAlreadyActive(f"User {self._user_id} is already active")
        self._assert_not_deleted()
        self._status = UserStatus.ACTIVE
        self._touch()
        self.record_event(UserActivated(user_id=self._user_id))

    def deactivate(self) -> None:
        """Deactivate the user.

        A pending, active, or suspended user becomes disabled.

        Raises:
            InvalidUserState: When the user is deleted or already disabled.
        """
        if self._status is UserStatus.DELETED:
            raise InvalidUserState(
                f"User {self._user_id} is deleted and cannot be deactivated"
            )
        if self._status is UserStatus.DISABLED:
            raise InvalidUserState(f"User {self._user_id} is already disabled")
        self._status = UserStatus.DISABLED
        self._touch()

    def suspend(self) -> None:
        """Suspend the user.

        Owners cannot be suspended.

        Raises:
            CannotSuspendOwner: When the user holds the OWNER role.
            InvalidUserState: When the user is deleted or already suspended.
        """
        if self._role is UserRole.OWNER:
            raise CannotSuspendOwner(f"Owner user {self._user_id} cannot be suspended")
        if self._status is UserStatus.DELETED:
            raise InvalidUserState(
                f"User {self._user_id} is deleted and cannot be suspended"
            )
        if self._status is UserStatus.SUSPENDED:
            raise InvalidUserState(f"User {self._user_id} is already suspended")
        self._status = UserStatus.SUSPENDED
        self._touch()
        self.record_event(UserSuspended(user_id=self._user_id))

    def restore(self) -> None:
        """Restore a suspended user to the active state.

        Raises:
            InvalidUserState: When the user is not currently suspended.
        """
        if self._status is not UserStatus.SUSPENDED:
            raise InvalidUserState(
                f"User {self._user_id} is not suspended and cannot be restored"
            )
        self._status = UserStatus.ACTIVE
        self._touch()

    def delete(self) -> None:
        """Delete the user.

        Deletion is terminal: no further state change is allowed afterwards.

        Raises:
            InvalidUserState: When the user is already deleted.
        """
        if self._status is UserStatus.DELETED:
            raise InvalidUserState(f"User {self._user_id} is already deleted")
        self._status = UserStatus.DELETED
        self._touch()
        self.record_event(UserDeleted(user_id=self._user_id))

    def update_metadata(self, new_metadata: Metadata) -> None:
        """Replace the user's metadata map.

        A no-op when the new metadata equals the current one.

        Args:
            new_metadata: The new metadata map.

        Raises:
            InvalidUserState: When the user is deleted.
        """
        self._assert_not_deleted()
        if new_metadata == self._metadata:
            return
        self._metadata = new_metadata
        self._touch()

    def increment_version(self) -> None:
        """Bump the optimistic-locking version by one patch.

        Domain methods bump the version automatically; call this directly only
        when an out-of-band change was applied to the aggregate.

        Raises:
            InvalidUserState: When the user is deleted.
        """
        self._assert_not_deleted()
        self._bump_version()

    def _assert_not_deleted(self) -> None:
        """Raise when the user is deleted.

        Raises:
            InvalidUserState: When the user is deleted.
        """
        if self._status is UserStatus.DELETED:
            raise InvalidUserState(
                f"User {self._user_id} is deleted and cannot be modified"
            )

    def _touch(self) -> None:
        """Refresh the update timestamp and bump the version."""
        self._updated_at = Timestamp.now()
        self._bump_version()

    def _bump_version(self) -> None:
        """Increment the optimistic-locking version by one patch."""
        self._version = Version(
            self._version.major,
            self._version.minor,
            self._version.patch + 1,
        )
