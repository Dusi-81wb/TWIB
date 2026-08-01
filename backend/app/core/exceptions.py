"""Application exception hierarchy.

Every application exception derives from :class:`TWIBException` and carries
an error code, a message, an HTTP status code, and optional details. The
global exception handlers in :mod:`app.core.handlers` translate these
exceptions into a consistent JSON response.

Only generic infrastructure exceptions are defined here. Domain-specific
exceptions (authentication, database, agents, workflows) belong in later
phases.
"""

from fastapi import status

from app.core.error_codes import (
    CONFLICT,
    FORBIDDEN,
    INTERNAL_SERVER_ERROR,
    RESOURCE_NOT_FOUND,
    SERVICE_UNAVAILABLE,
    UNAUTHORIZED,
    VALIDATION_ERROR,
)


class TWIBException(Exception):
    """Base exception for all application errors.

    Attributes:
        message: Human-readable description of the error.
        error_code: Stable machine-readable code identifying the error.
        status_code: HTTP status code returned to the client.
        details: Optional structured information about the error.
    """

    error_code: str = INTERNAL_SERVER_ERROR
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self,
        message: str,
        *,
        details: dict | None = None,
        error_code: str | None = None,
        status_code: int | None = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable description of the error.
            details: Optional structured information about the error.
            error_code: Overrides the class-level error code when provided.
            status_code: Overrides the class-level status code when provided.
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.error_code
        self.status_code = status_code or self.status_code
        self.details = details or {}


class ValidationException(TWIBException):
    """Raised when input validation fails."""

    error_code: str = VALIDATION_ERROR
    status_code: int = status.HTTP_400_BAD_REQUEST


class UnauthorizedException(TWIBException):
    """Raised when a request lacks valid credentials."""

    error_code: str = UNAUTHORIZED
    status_code: int = status.HTTP_401_UNAUTHORIZED


class ForbiddenException(TWIBException):
    """Raised when a request is not permitted to perform an action."""

    error_code: str = FORBIDDEN
    status_code: int = status.HTTP_403_FORBIDDEN


class NotFoundException(TWIBException):
    """Raised when a requested resource does not exist."""

    error_code: str = RESOURCE_NOT_FOUND
    status_code: int = status.HTTP_404_NOT_FOUND


class ConflictException(TWIBException):
    """Raised when a request conflicts with the current resource state."""

    error_code: str = CONFLICT
    status_code: int = status.HTTP_409_CONFLICT


class ServiceUnavailableException(TWIBException):
    """Raised when an external dependency is temporarily unavailable."""

    error_code: str = SERVICE_UNAVAILABLE
    status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE


class InternalServerException(TWIBException):
    """Raised when an unexpected internal failure occurs."""

    error_code: str = INTERNAL_SERVER_ERROR
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
