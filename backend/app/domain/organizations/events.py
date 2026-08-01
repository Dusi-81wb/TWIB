"""Organization domain events.

These events record the meaningful things that happen to an organization
aggregate. They subclass :class:`~app.domain.event.DomainEvent`, so every
occurrence carries a unique ``event_id`` and a UTC ``occurred_at`` timestamp.

The aggregate only records events through
:meth:`~app.domain.aggregate.AggregateRoot.record_event`; publishing belongs
to outer layers. No event bus exists in this phase.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.event import DomainEvent
from app.domain.organizations.plan import SubscriptionPlan
from app.domain.users.role import UserRole
from app.domain.value_objects import Name, UuidIdentity


@dataclass(frozen=True, kw_only=True, eq=False, repr=False)
class OrganizationCreated(DomainEvent):
    """Recorded when an organization aggregate is created."""

    organization_id: UuidIdentity


@dataclass(frozen=True, kw_only=True, eq=False, repr=False)
class OrganizationRenamed(DomainEvent):
    """Recorded when an organization is renamed."""

    organization_id: UuidIdentity
    name: Name
    previous_name: Name


@dataclass(frozen=True, kw_only=True, eq=False, repr=False)
class OrganizationActivated(DomainEvent):
    """Recorded when an organization is activated."""

    organization_id: UuidIdentity


@dataclass(frozen=True, kw_only=True, eq=False, repr=False)
class OrganizationSuspended(DomainEvent):
    """Recorded when an organization is suspended."""

    organization_id: UuidIdentity


@dataclass(frozen=True, kw_only=True, eq=False, repr=False)
class MemberAdded(DomainEvent):
    """Recorded when a member is added to an organization."""

    organization_id: UuidIdentity
    user_id: UuidIdentity
    role: UserRole


@dataclass(frozen=True, kw_only=True, eq=False, repr=False)
class MemberRemoved(DomainEvent):
    """Recorded when a member is removed from an organization."""

    organization_id: UuidIdentity
    user_id: UuidIdentity


@dataclass(frozen=True, kw_only=True, eq=False, repr=False)
class OwnerChanged(DomainEvent):
    """Recorded when the organization owner changes."""

    organization_id: UuidIdentity
    owner_id: UuidIdentity
    previous_owner_id: UuidIdentity


@dataclass(frozen=True, kw_only=True, eq=False, repr=False)
class PlanChanged(DomainEvent):
    """Recorded when the organization subscription plan changes."""

    organization_id: UuidIdentity
    plan: SubscriptionPlan
    previous_plan: SubscriptionPlan
