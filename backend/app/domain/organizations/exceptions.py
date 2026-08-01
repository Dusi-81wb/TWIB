"""Organization domain exceptions.

These exceptions express the business rules of the organization aggregate.
They are framework-independent and subclass :class:`BusinessRuleViolation`, so
outer layers (application services, API) can translate them into their own
error contract.
"""

from __future__ import annotations

from app.domain.exceptions import BusinessRuleViolation


class DuplicateMember(BusinessRuleViolation):
    """Raised when a user who is already an active member is added again."""


class OwnerCannotBeRemoved(BusinessRuleViolation):
    """Raised when an attempt is made to remove the organization owner."""


class InvalidOrganizationState(BusinessRuleViolation):
    """Raised when an operation is not valid in the current organization state."""


class OrganizationArchived(BusinessRuleViolation):
    """Raised when an archived organization is modified or archived again."""


class MembershipAlreadyExists(BusinessRuleViolation):
    """Raised when a pending membership already exists for a user."""
