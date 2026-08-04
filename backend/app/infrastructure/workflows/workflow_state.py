"""WorkflowState alias module."""

from app.workflows.workflow_state import (
    StateHistoryEntry,
    WorkflowState,
    validate_state_transition,
)

__all__ = [
    "StateHistoryEntry",
    "WorkflowState",
    "validate_state_transition",
]
