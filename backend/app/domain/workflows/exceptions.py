"""Domain exceptions for the Workflow Subsystem.

Defines custom exception hierarchy for workflow validation, cycles, execution errors,
state transition violations, and checkpoint rejections.
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


class WorkflowDomainError(TWIBException):
    """Base exception for all workflow domain errors."""

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
        extra_details = details or {}
        extra_details["workflow_id"] = workflow_id
        super().__init__(
            message,
            details=extra_details,
            error_code=error_code,
            status_code=status_code,
        )
        self.workflow_id = workflow_id


class WorkflowNotFoundError(WorkflowDomainError):
    """Raised when a requested workflow or execution cannot be found."""

    error_code: str = RESOURCE_NOT_FOUND
    status_code: int = status.HTTP_404_NOT_FOUND

    def __init__(self, message: str, workflow_id: str | None = None) -> None:
        super().__init__(message, workflow_id=workflow_id or "unknown", status_code=status.HTTP_404_NOT_FOUND)


class WorkflowValidationError(WorkflowDomainError):
    """Raised when a workflow graph or node definition fails structural validation."""

    error_code: str = VALIDATION_ERROR
    status_code: int = status.HTTP_400_BAD_REQUEST

    def __init__(
        self,
        message: str,
        workflow_id: str | None = None,
        errors: list[str] | None = None,
    ) -> None:
        errs = errors or []
        super().__init__(
            message,
            workflow_id=workflow_id or "unknown",
            details={"errors": errs},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
        self.errors = errs


class WorkflowCycleError(WorkflowValidationError):
    """Raised specifically when a directed cycle is detected in the Workflow DAG."""

    def __init__(self, cycle_path: list[str], workflow_id: str | None = None) -> None:
        path_str = " -> ".join(cycle_path)
        message = f"Cyclic dependency detected in workflow DAG: {path_str}"
        super().__init__(message, workflow_id=workflow_id, errors=[message])
        self.cycle_path = cycle_path


class WorkflowStateError(WorkflowDomainError):
    """Raised when an illegal workflow state transition is attempted."""

    error_code: str = "INVALID_STATE"
    status_code: int = status.HTTP_400_BAD_REQUEST

    def __init__(
        self,
        message: str,
        workflow_id: str | None = None,
        from_state: str | None = None,
        to_state: str | None = None,
    ) -> None:
        super().__init__(
            message,
            workflow_id=workflow_id or "unknown",
            details={"from_state": from_state, "to_state": to_state},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
        self.from_state = from_state
        self.to_state = to_state


class WorkflowExecutionError(WorkflowDomainError):
    """Raised when workflow execution encounters a fatal unrecoverable error."""

    def __init__(
        self,
        message: str,
        workflow_id: str | None = None,
        step_id: str | None = None,
        original_error: Exception | None = None,
    ) -> None:
        super().__init__(
            message,
            workflow_id=workflow_id or "unknown",
            details={
                "step_id": step_id,
                "original_error": str(original_error) if original_error else None,
            },
        )
        self.step_id = step_id
        self.original_error = original_error


class NodeExecutionError(WorkflowExecutionError):
    """Raised when a specific node fails execution beyond allowed retries."""

    def __init__(
        self,
        message: str,
        node_id: str,
        workflow_id: str | None = None,
        attempt: int = 1,
        cause: Exception | None = None,
        retryable: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            message,
            workflow_id=workflow_id,
            step_id=node_id,
            original_error=cause,
        )
        self.node_id = node_id
        self.attempt = attempt
        self.cause = cause
        self.retryable = retryable



class CheckpointError(WorkflowDomainError):
    """Raised when an approval checkpoint operation fails."""

    def __init__(
        self,
        message: str,
        checkpoint_id: str | None = None,
        workflow_id: str | None = None,
    ) -> None:
        super().__init__(
            message,
            workflow_id=workflow_id or "unknown",
            details={"checkpoint_id": checkpoint_id},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
        self.checkpoint_id = checkpoint_id
