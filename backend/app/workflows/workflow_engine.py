"""Workflow Engine Core implementation.

Central orchestration layer for managing workflow lifecycles (create, load, validate,
start, cancel). Reuses SupervisorAgent for multi-agent coordination without executing
agent logic directly during lifecycle setup.
"""

from __future__ import annotations

from typing import Any

from app.agents.supervisor_agent import SupervisorAgent
from app.workflows.workflow import Workflow
from app.workflows.workflow_exceptions import (
    WorkflowNotFoundError,
    WorkflowValidationError,
)
from app.workflows.workflow_models import (
    WorkflowStatus,
    WorkflowStep,
)


class WorkflowEngine:
    """Workflow Engine core orchestrator.

    Manages workflow registration, state transitions, validation,
    and execution lifecycle.
    """

    def __init__(
        self,
        supervisor_agent: SupervisorAgent | None = None,
    ) -> None:
        """Initialize WorkflowEngine.

        Args:
            supervisor_agent: Optional SupervisorAgent for multi-agent coordination.
        """
        self._supervisor_agent = supervisor_agent or SupervisorAgent()
        self._workflows: dict[str, Workflow] = {}

    @property
    def supervisor(self) -> SupervisorAgent:
        """Return attached SupervisorAgent instance."""
        return self._supervisor_agent

    def create_workflow(
        self,
        workflow_name: str,
        user_request: str,
        steps: list[WorkflowStep] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Workflow:
        """Create and register a new Workflow instance.

        Args:
            workflow_name: Name of the workflow.
            user_request: Original user goal or prompt.
            steps: Optional pre-configured execution steps.
            metadata: Optional arbitrary workflow metadata.

        Returns:
            Registered Workflow instance.

        Raises:
            WorkflowValidationError: If workflow_name or user_request is empty.
        """
        if not workflow_name or not workflow_name.strip():
            raise WorkflowValidationError(
                "Workflow name cannot be empty",
                workflow_id="unknown",
            )
        if not user_request or not user_request.strip():
            raise WorkflowValidationError(
                "User request prompt cannot be empty",
                workflow_id="unknown",
            )

        workflow = Workflow(
            workflow_name=workflow_name.strip(),
            user_request=user_request.strip(),
            execution_steps=steps,
            metadata=metadata,
        )
        self._workflows[workflow.workflow_id] = workflow
        return workflow

    def load_workflow(self, workflow_id: str) -> Workflow:
        """Load an existing workflow by its unique ID.

        Args:
            workflow_id: Unique workflow instance identifier.

        Returns:
            Loaded Workflow instance.

        Raises:
            WorkflowNotFoundError: If workflow ID is not found.
        """
        if workflow_id not in self._workflows:
            raise WorkflowNotFoundError(
                f"Workflow with ID '{workflow_id}' not found",
                workflow_id=workflow_id,
            )
        return self._workflows[workflow_id]

    def validate_workflow(self, workflow: Workflow) -> bool:
        """Validate workflow structure and state transitions.

        Args:
            workflow: Target Workflow instance.

        Returns:
            True if workflow is valid.

        Raises:
            WorkflowValidationError: If workflow validation fails.
        """
        if not workflow.workflow_name or not workflow.workflow_name.strip():
            raise WorkflowValidationError(
                "Workflow validation failed: name is empty",
                workflow_id=workflow.workflow_id,
            )
        if not workflow.user_request or not workflow.user_request.strip():
            raise WorkflowValidationError(
                "Workflow validation failed: user_request is empty",
                workflow_id=workflow.workflow_id,
            )

        # Mark ready if currently in CREATED status
        if workflow.workflow_status == WorkflowStatus.CREATED:
            workflow.mark_ready()

        return True

    def start_workflow(self, workflow_id: str) -> Workflow:
        """Start a registered workflow by transitioning its status to RUNNING.

        Note: Does NOT execute agent logic directly in Phase 8.1.

        Args:
            workflow_id: Unique identifier of the workflow to start.

        Returns:
            Updated Workflow instance.

        Raises:
            WorkflowNotFoundError: If workflow is not registered.
            WorkflowValidationError: If workflow validation fails.
        """
        workflow = self.load_workflow(workflow_id)
        self.validate_workflow(workflow)
        workflow.mark_running()
        return workflow

    def cancel_workflow(self, workflow_id: str) -> Workflow:
        """Cancel a registered workflow by transitioning its status to CANCELLED.

        Args:
            workflow_id: Unique identifier of the workflow to cancel.

        Returns:
            Updated Workflow instance.

        Raises:
            WorkflowNotFoundError: If workflow is not registered.
        """
        workflow = self.load_workflow(workflow_id)
        workflow.mark_cancelled()
        return workflow
