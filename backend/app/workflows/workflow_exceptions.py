"""Workflow exceptions hierarchy.

Defines exceptions for the Workflow Engine framework. All exceptions derive from
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


class WorkflowError(TWIBException):
    """Base exception for all workflow engine errors."""

    error_code: str = INTERNAL_SERVER_ERROR
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self,
        message: str,
        *,
        workflow_id: str = "unknown",
        details: dict[str, Any] | None = None,
        error_code: str | None = None,
        status_code: int | None = None,
    ) -> None:
        """Initialize WorkflowError.

        Args:
            message: Human-readable error description.
            workflow_id: Identifier of the workflow experiencing the error.
            details: Optional structured details.
            error_code: Optional override error code.
            status_code: Optional override status code.
        """
        extra_details = details or {}
        extra_details["workflow_id"] = workflow_id
        super().__init__(
            message,
            details=extra_details,
            error_code=error_code,
            status_code=status_code,
        )
        self.workflow_id = workflow_id


class WorkflowValidationError(WorkflowError):
    """Raised when a workflow model or request fails validation rules."""

    error_code: str = VALIDATION_ERROR
    status_code: int = status.HTTP_400_BAD_REQUEST


class WorkflowNotFoundError(WorkflowError):
    """Raised when a requested workflow ID cannot be found."""

    error_code: str = RESOURCE_NOT_FOUND
    status_code: int = status.HTTP_404_NOT_FOUND


class WorkflowStateError(WorkflowError):
    """Raised when an invalid workflow state transition is attempted."""

    error_code: str = VALIDATION_ERROR
    status_code: int = status.HTTP_400_BAD_REQUEST


class WorkflowExecutionError(WorkflowError):
    """Raised when a workflow execution encounters an unrecoverable failure."""

    error_code: str = INTERNAL_SERVER_ERROR
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
