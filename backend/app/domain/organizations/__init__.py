"""Organization domain package.

This package models the organization aggregate, the tenant boundary of TWIB.
It contains the :class:`~app.domain.organizations.organization.Organization`
aggregate root, the immutable
:class:`~app.domain.organizations.membership.OrganizationMembership` domain
object with its :class:`~app.domain.organizations.membership.MembershipStatus`
enum, the :class:`~app.domain.organizations.status.OrganizationStatus` and
:class:`~app.domain.organizations.plan.SubscriptionPlan` domain enums, the
organization domain events, and the organization business-rule exceptions.

Everything here is pure Python (standard library only) and depends on the
Phase 2.1 domain foundation, the Phase 2.2 value objects, and the Phase 2.3
user domain. It contains no authentication, database, billing, repository, or
API code.
"""

from __future__ import annotations

from app.domain.organizations.events import (
    MemberAdded,
    MemberRemoved,
    OrganizationActivated,
    OrganizationCreated,
    OrganizationRenamed,
    OrganizationSuspended,
    OwnerChanged,
    PlanChanged,
)
from app.domain.organizations.exceptions import (
    DuplicateMember,
    InvalidOrganizationState,
    MembershipAlreadyExists,
    OrganizationArchived,
    OwnerCannotBeRemoved,
)
from app.domain.organizations.membership import (
    MembershipStatus,
    OrganizationMembership,
)
from app.domain.organizations.organization import Organization
from app.domain.organizations.plan import SubscriptionPlan
from app.domain.organizations.status import OrganizationStatus

__all__ = [
    "DuplicateMember",
    "InvalidOrganizationState",
    "MemberAdded",
    "MemberRemoved",
    "MembershipAlreadyExists",
    "MembershipStatus",
    "Organization",
    "OrganizationActivated",
    "OrganizationArchived",
    "OrganizationCreated",
    "OrganizationMembership",
    "OrganizationRenamed",
    "OrganizationStatus",
    "OrganizationSuspended",
    "OwnerCannotBeRemoved",
    "OwnerChanged",
    "PlanChanged",
    "SubscriptionPlan",
]
