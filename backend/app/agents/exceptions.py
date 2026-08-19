"""Agent exception hierarchy.

Defines exceptions for the Agent Core framework. All exceptions derive from
:class:`~app.core.exceptions.TWIBException`.
"""

from __future__ import annotations

from typing import Any

from fastapi import status

from app.core.error_codes import (
    INTERNAL_SERVER_ERROR,
    RESOURCE_NOT_FOUND,
    VALIDATION_ERROR,
)
from app.core.exceptions import TWIBException


class AgentError(TWIBException):
    """Base exception for all agent framework errors."""

    error_code: str = INTERNAL_SERVER_ERROR
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self,
        message: str,
        *,
        agent_id: str = "unknown",
        details: dict[str, Any] | None = None,
        error_code: str | None = None,
        status_code: int | None = None,
    ) -> None:
        """Initialize AgentError.

        Args:
            message: Human-readable error description.
            agent_id: Identifier of the agent experiencing the error.
            details: Optional structured details.
            error_code: Optional override error code.
            status_code: Optional override status code.
        """
        extra_details = details or {}
        extra_details["agent_id"] = agent_id
        super().__init__(
            message,
            details=extra_details,
            error_code=error_code,
            status_code=status_code,
        )
        self.agent_id = agent_id


class AgentExecutionError(AgentError):
    """Raised when an agent execution encounters an unrecoverable failure."""

    error_code: str = INTERNAL_SERVER_ERROR
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR


class AgentValidationError(AgentError):
    """Raised when agent input or output validation fails."""

    error_code: str = VALIDATION_ERROR
    status_code: int = status.HTTP_400_BAD_REQUEST


class AgentNotFoundError(AgentError):
    """Raised when an agent is requested but not registered."""

    error_code: str = RESOURCE_NOT_FOUND
    status_code: int = status.HTTP_404_NOT_FOUND
