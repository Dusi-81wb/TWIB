"""User domain events.

These events record the meaningful things that happen to a user aggregate.
They subclass :class:`~app.domain.event.DomainEvent`, so every occurrence
carries a unique ``event_id`` and a UTC ``occurred_at`` timestamp.

The aggregate only records events through
:meth:`~app.domain.aggregate.AggregateRoot.record_event`; publishing belongs
to outer layers. No event bus exists in this phase.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.event import DomainEvent
from app.domain.value_objects import Email, Name, UuidIdentity


@dataclass(frozen=True, kw_only=True, eq=False, repr=False)
class UserCreated(DomainEvent):
    """Recorded when a user aggregate is created."""

    user_id: UuidIdentity


@dataclass(frozen=True, kw_only=True, eq=False, repr=False)
class UserActivated(DomainEvent):
    """Recorded when a user is activated."""

    user_id: UuidIdentity


@dataclass(frozen=True, kw_only=True, eq=False, repr=False)
class UserSuspended(DomainEvent):
    """Recorded when a user is suspended."""

    user_id: UuidIdentity


@dataclass(frozen=True, kw_only=True, eq=False, repr=False)
class UserDeleted(DomainEvent):
    """Recorded when a user is deleted."""

    user_id: UuidIdentity


@dataclass(frozen=True, kw_only=True, eq=False, repr=False)
class UserEmailChanged(DomainEvent):
    """Recorded when a user's email address changes."""

    user_id: UuidIdentity
    email: Email
    previous_email: Email


@dataclass(frozen=True, kw_only=True, eq=False, repr=False)
class UserNameChanged(DomainEvent):
    """Recorded when a user's display name changes."""

    user_id: UuidIdentity
    display_name: Name
    previous_display_name: Name
