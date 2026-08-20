"""Workflow exceptions hierarchy.

Defines exceptions for the Workflow Engine framework, aliased to domain exceptions.
"""

from __future__ import annotations

from app.domain.workflows.exceptions import (
    CheckpointError,
    NodeExecutionError,
    WorkflowCycleError,
    WorkflowDomainError,
    WorkflowDomainError as WorkflowError,
    WorkflowExecutionError,
    WorkflowNotFoundError,
    WorkflowStateError,
    WorkflowValidationError,
)

__all__ = [
    "CheckpointError",
    "NodeExecutionError",
    "WorkflowCycleError",
    "WorkflowDomainError",
    "WorkflowError",
    "WorkflowExecutionError",
    "WorkflowNotFoundError",
    "WorkflowStateError",
    "WorkflowValidationError",
]
