"""Workspace domain exceptions.

These exceptions express the business rules of the workspace aggregate. They
are framework-independent and subclass :class:`BusinessRuleViolation`, so outer
layers (application services, API) can translate them into their own error
contract.
"""

from __future__ import annotations

from app.domain.exceptions import BusinessRuleViolation


class WorkspaceArchived(BusinessRuleViolation):
    """Raised when an archived workspace is modified or archived again."""


class WorkspaceAlreadyExists(BusinessRuleViolation):
    """Raised when a workspace with the same identity already exists.

    This rule requires knowledge of other workspaces, so it is raised by the
    application/repository layer when workspace uniqueness is enforced (for
    example on a shared slug); the aggregate itself cannot detect it.
    """


class DuplicateWorkspaceMember(BusinessRuleViolation):
    """Raised when a user who is already a member is added again."""


class OwnerCannotBeRemoved(BusinessRuleViolation):
    """Raised when an attempt is made to remove the workspace owner."""


class InvalidWorkspaceState(BusinessRuleViolation):
    """Raised when an operation is not valid in the current workspace state."""
