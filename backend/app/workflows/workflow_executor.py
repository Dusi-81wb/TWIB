"""Workflow Executor implementation.

Delegates workflow execution to the SupervisorAgent and manages execution state,
step outputs, failures, and event extension hooks.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from app.agents.models import AgentRequest, AgentStatus
from app.agents.supervisor_agent import SupervisorAgent
from app.workflows.workflow import Workflow
from app.workflows.workflow_engine import WorkflowEngine
from app.workflows.workflow_exceptions import (
    WorkflowExecutionError,
    WorkflowStateError,
    WorkflowValidationError,
)
from app.workflows.workflow_models import (
    WorkflowStatus,
    WorkflowStep,
)


class WorkflowExecutor:
    """Workflow Executor for delegating execution to SupervisorAgent.

    Manages workflow lifecycle transitions during execution, updates step records,
    handles failure boundaries without exposing internal stack traces.
    """

    def __init__(
        self,
        engine: WorkflowEngine | None = None,
        supervisor_agent: SupervisorAgent | None = None,
        event_listener: Callable[[str, dict[str, Any]], None] | None = None,
    ) -> None:
        """Initialize WorkflowExecutor.

        Args:
            engine: Optional custom WorkflowEngine instance.
            supervisor_agent: Optional custom SupervisorAgent instance.
            event_listener: Optional event hook callback (event_type, payload).
        """
        self._engine = engine or WorkflowEngine(supervisor_agent=supervisor_agent)
        self._supervisor = supervisor_agent or self._engine.supervisor
        self._event_listener = event_listener

    @property
    def engine(self) -> WorkflowEngine:
        """Return attached WorkflowEngine instance."""
        return self._engine

    @property
    def supervisor(self) -> SupervisorAgent:
        """Return attached SupervisorAgent instance."""
        return self._supervisor

    async def execute(
        self,
        workflow_or_id: Workflow | str,
        context: dict[str, Any] | None = None,
    ) -> Workflow:
        """Execute a complete workflow using the SupervisorAgent pipeline.

        Args:
            workflow_or_id: Workflow domain instance or workflow_id string.
            context: Optional context dictionary overrides.

        Returns:
            Executed Workflow domain instance.

        Raises:
            WorkflowNotFoundError: If workflow ID cannot be found.
            WorkflowValidationError: If workflow validation fails.
            WorkflowExecutionError: If execution fails catastrophically.
        """
        workflow = self._resolve_workflow(workflow_or_id)

        # Validate workflow before starting
        self._engine.validate_workflow(workflow)
        workflow.mark_running()
        self._emit_event("workflow.started", {"workflow_id": workflow.workflow_id})

        # Construct AgentRequest payload for SupervisorAgent
        merged_ctx = dict(workflow.metadata.get("context", {}))
        if context:
            merged_ctx.update(context)

        agent_req = AgentRequest(
            agent_id=self._supervisor.metadata.id,
            user_prompt=workflow.user_request,
            context=merged_ctx,
            model=merged_ctx.get("model"),
            provider=merged_ctx.get("provider"),
        )

        step_start = datetime.now(UTC)
        try:
            sup_res = await self._supervisor.execute(agent_req)
        except Exception as err:
            err_msg = f"Supervisor execution error: {err}"
            workflow.mark_failed(err_msg)
            self._emit_event(
                "workflow.failed",
                {"workflow_id": workflow.workflow_id, "error": err_msg},
            )
            raise WorkflowExecutionError(
                err_msg,
                workflow_id=workflow.workflow_id,
            ) from err

        # Process supervisor execution steps & update workflow state
        sup_dict = sup_res.result or {}
        executed_steps = sup_dict.get("executed_steps", [])

        # Update execution_steps on workflow entity
        new_steps: list[WorkflowStep] = []
        for raw_step in executed_steps:
            agent_id = raw_step.get("agent_id", "unknown")
            node_id = raw_step.get("node_id")
            step_status = (
                WorkflowStatus.COMPLETED
                if raw_step.get("status") == AgentStatus.COMPLETED
                else WorkflowStatus.FAILED
            )
            step_name = f"Execute {agent_id.capitalize()} Node ({node_id})" if node_id else f"Execute {agent_id.capitalize()} Agent"
            step_obj = WorkflowStep(
                name=step_name,
                agent_id=agent_id,
                status=step_status,
                input_data={"objective": workflow.user_request, "node_id": node_id},
                output_data=raw_step.get("result"),
                error=raw_step.get("error"),
                started_at=step_start,
                completed_at=datetime.now(UTC),
            )
            new_steps.append(step_obj)

        workflow.execution_steps = new_steps
        workflow.metadata["final_result"] = sup_dict.get("final_result")
        workflow.metadata["total_duration_seconds"] = sup_dict.get(
            "total_duration_seconds"
        )
        if "dag_plan" in sup_dict:
            workflow.metadata["dag_plan"] = sup_dict["dag_plan"]
        if "execution_graph" in sup_dict:
            workflow.metadata["execution_graph"] = sup_dict["execution_graph"]

        if sup_res.status == AgentStatus.COMPLETED:
            workflow.mark_completed()
            self._emit_event(
                "workflow.completed",
                {
                    "workflow_id": workflow.workflow_id,
                    "result": sup_dict.get("final_result"),
                },
            )
        else:
            failure_reason = (
                sup_res.error or "Supervisor execution reported step failures."
            )
            workflow.mark_failed(failure_reason)
            self._emit_event(
                "workflow.failed",
                {"workflow_id": workflow.workflow_id, "error": failure_reason},
            )

        return workflow

    async def execute_step(
        self,
        workflow_or_id: Workflow | str,
        step_id: str,
    ) -> Workflow:
        """Execute a specific single step within a workflow.

        Args:
            workflow_or_id: Workflow domain instance or workflow_id string.
            step_id: Identifier of the step or target agent_id to execute.

        Returns:
            Updated Workflow domain instance.

        Raises:
            WorkflowNotFoundError: If workflow ID is missing.
            WorkflowExecutionError: If step execution fails.
        """
        workflow = self._resolve_workflow(workflow_or_id)
        target_step = next(
            (
                s
                for s in workflow.execution_steps
                if s.step_id == step_id or s.agent_id == step_id
            ),
            None,
        )

        if not target_step:
            target_step = WorkflowStep(
                step_id=step_id,
                name=f"Execute {step_id}",
                agent_id=step_id,
            )
            workflow.add_step(target_step)

        if workflow.workflow_status != WorkflowStatus.RUNNING:
            workflow.mark_running()

        target_step.status = WorkflowStatus.RUNNING
        target_step.started_at = datetime.now(UTC)
        self._emit_event(
            "workflow.step.started",
            {"step_id": step_id, "workflow_id": workflow.workflow_id},
        )

        # Delegate execution to supervisor with single agent pipeline context
        agent_req = AgentRequest(
            agent_id=self._supervisor.metadata.id,
            user_prompt=workflow.user_request,
            context={"agent_pipeline": [target_step.agent_id or step_id]},
        )

        try:
            sup_res = await self._supervisor.execute(agent_req)
            sup_dict = sup_res.result or {}

            if sup_res.status == AgentStatus.COMPLETED:
                target_step.status = WorkflowStatus.COMPLETED
                target_step.output_data = sup_dict.get("final_result")
                target_step.completed_at = datetime.now(UTC)
                self._emit_event(
                    "workflow.step.completed",
                    {"step_id": step_id, "workflow_id": workflow.workflow_id},
                )
            else:
                target_step.status = WorkflowStatus.FAILED
                target_step.error = sup_res.error or "Step execution failed."
                target_step.completed_at = datetime.now(UTC)
                workflow.mark_failed(target_step.error)
                self._emit_event(
                    "workflow.step.failed",
                    {"step_id": step_id, "error": target_step.error},
                )
        except Exception as err:
            err_msg = f"Step '{step_id}' execution failed: {err}"
            target_step.status = WorkflowStatus.FAILED
            target_step.error = err_msg
            target_step.completed_at = datetime.now(UTC)
            workflow.mark_failed(err_msg)
            raise WorkflowExecutionError(
                err_msg, workflow_id=workflow.workflow_id
            ) from err

        return workflow

    def stop_execution(self, workflow_or_id: Workflow | str) -> Workflow:
        """Stop/cancel an in-flight workflow execution.

        Args:
            workflow_or_id: Workflow domain instance or workflow_id string.

        Returns:
            Cancelled Workflow domain instance.
        """
        workflow = self._resolve_workflow(workflow_or_id)
        workflow.mark_cancelled()
        self._emit_event("workflow.cancelled", {"workflow_id": workflow.workflow_id})
        return workflow

    def pause_execution(self, workflow_or_id: Workflow | str) -> Workflow:
        """Pause an in-flight workflow execution.

        Args:
            workflow_or_id: Workflow domain instance or workflow_id string.

        Returns:
            Paused Workflow domain instance.
        """
        workflow = self._resolve_workflow(workflow_or_id)
        workflow.mark_paused()
        self._emit_event("workflow.paused", {"workflow_id": workflow.workflow_id})
        return workflow

    async def resume_execution(self, workflow_or_id: Workflow | str) -> Workflow:
        """Resume execution of a paused workflow.

        Args:
            workflow_or_id: Workflow domain instance or workflow_id string.

        Returns:
            Resumed Workflow domain instance.
        """
        workflow = self._resolve_workflow(workflow_or_id)
        if workflow.workflow_status != WorkflowStatus.PAUSED:
            err_msg = (
                f"Cannot resume workflow in status '{workflow.workflow_status}'; "
                "must be PAUSED"
            )
            raise WorkflowStateError(
                err_msg,
                workflow_id=workflow.workflow_id,
            )
        self._emit_event("workflow.resumed", {"workflow_id": workflow.workflow_id})
        return await self.execute(workflow)

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    def _resolve_workflow(self, workflow_or_id: Workflow | str) -> Workflow:
        """Resolve Workflow instance from input parameter."""
        if isinstance(workflow_or_id, Workflow):
            return workflow_or_id
        if isinstance(workflow_or_id, str):
            return self._engine.load_workflow(workflow_or_id)
        raise WorkflowValidationError("Invalid workflow reference provided")

    def _emit_event(self, event_type: str, payload: dict[str, Any]) -> None:
        """Event publisher extension point hook."""
        if self._event_listener is not None:
            import contextlib

            with contextlib.suppress(Exception):
                self._event_listener(event_type, payload)
