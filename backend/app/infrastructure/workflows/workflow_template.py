"""WorkflowTemplate alias module."""

from app.workflows.workflow_template import (
    WorkflowTemplate,
    get_builtin_templates,
)

__all__ = [
    "WorkflowTemplate",
    "get_builtin_templates",
]
