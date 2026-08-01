"""Domain-specific exception hierarchy.

These exceptions are framework-independent and carry no knowledge of HTTP,
databases, or external services. They signal violations of the enterprise
business rules inside the domain layer. Outer layers (application services,
API) may translate them into their own error contract.

Every exception derives from :class:`DomainException`.
"""

from __future__ import annotations

from typing import Any


class DomainException(Exception):
    """Base exception for all domain errors.

    Attributes:
        message: Human-readable description of the domain error.
        details: Optional structured information about the error.
    """

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the domain exception.

        Args:
            message: Human-readable description of the domain error.
            details: Optional structured information about the error.
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class BusinessRuleViolation(DomainException):
    """Raised when an enterprise business rule or domain invariant is violated."""


class EntityNotFound(DomainException):
    """Raised when a requested entity does not exist."""


class InvalidOperation(DomainException):
    """Raised when an operation is not valid in the current state."""


class InvalidValue(DomainException):
    """Raised when a value object is constructed with an invalid value."""
