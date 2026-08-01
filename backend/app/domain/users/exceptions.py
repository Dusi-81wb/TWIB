"""User domain exceptions.

These exceptions express the business rules of the user aggregate. They are
framework-independent and subclass :class:`BusinessRuleViolation`, so outer
layers (application services, API) can translate them into their own error
contract.
"""

from __future__ import annotations

from app.domain.exceptions import BusinessRuleViolation


class InvalidUserState(BusinessRuleViolation):
    """Raised when an operation is not valid in the current user state."""


class EmailAlreadyAssigned(BusinessRuleViolation):
    """Raised when an email is already assigned to a user."""


class CannotSuspendOwner(BusinessRuleViolation):
    """Raised when an attempt is made to suspend an owner user."""


class UserAlreadyActive(BusinessRuleViolation):
    """Raised when an already-active user is activated again."""
