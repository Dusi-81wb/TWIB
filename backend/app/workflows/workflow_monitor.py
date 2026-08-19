"""Workflow Monitor implementation for runtime metrics computation.

Inspects registered Workflow instances and execution steps to compute real-time
workflow metrics, agent execution metrics, and detailed workflow diagnostics.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from app.workflows.workflow_engine import WorkflowEngine
from app.workflows.workflow_models import WorkflowStatus


class WorkflowMetricsSummary(BaseModel):
    """Aggregated workflow execution metrics."""

    total_workflows: int = Field(default=0, description="Total workflows registered.")
    running_workflows: int = Field(
        default=0, description="Workflows currently running."
    )
    completed_workflows: int = Field(
        default=0, description="Workflows completed successfully."
    )
    failed_workflows: int = Field(default=0, description="Workflows failed.")
    paused_workflows: int = Field(
        default=0, description="Workflows currently paused or waiting approval."
    )
    average_execution_time_seconds: float = Field(
        default=0.0, description="Average execution duration in seconds."
    )
    success_rate: float = Field(
        default=100.0, description="Workflow success rate percentage (0.0 - 100.0)."
    )


class AgentMetricsSummary(BaseModel):
    """Aggregated metrics across AI agents."""

    executions_per_agent: dict[str, int] = Field(
        default_factory=dict, description="Total execution count per agent ID."
    )
    successful_executions: dict[str, int] = Field(
        default_factory=dict, description="Successful execution count per agent ID."
    )
    failed_executions: dict[str, int] = Field(
        default_factory=dict, description="Failed execution count per agent ID."
    )
    average_execution_duration_seconds: dict[str, float] = Field(
        default_factory=dict,
        description="Average execution duration in seconds per agent ID.",
    )
    last_execution_time: dict[str, str | None] = Field(
        default_factory=dict,
        description="ISO 8601 timestamp of last execution per agent ID.",
    )


class WorkflowMonitoringDetails(BaseModel):
    """Detailed runtime diagnostic snapshot for an individual workflow."""

    workflow_id: str
    workflow_name: str
    current_state: str
    current_step: str | None = None
    executed_agents: list[str] = Field(default_factory=list)
    execution_history: list[dict[str, Any]] = Field(default_factory=list)
    created_at: str
    updated_at: str
    duration_seconds: float


class WorkflowMonitor:
    """Monitor for evaluating live Workflow and Agent metrics."""

    def __init__(self, engine: WorkflowEngine) -> None:
        """Initialize WorkflowMonitor with WorkflowEngine instance."""
        self._engine = engine

    def get_workflow_metrics(self) -> WorkflowMetricsSummary:
        """Compute aggregated workflow execution metrics."""
        workflows = list(self._engine._workflows.values())
        total = len(workflows)
        if total == 0:
            return WorkflowMetricsSummary()

        running = 0
        completed = 0
        failed = 0
        paused = 0
        durations: list[float] = []

        for wf in workflows:
            status_val = (
                wf.workflow_status.value
                if hasattr(wf.workflow_status, "value")
                else str(wf.workflow_status)
            )
            if status_val == WorkflowStatus.RUNNING.value:
                running += 1
            elif status_val == WorkflowStatus.COMPLETED.value:
                completed += 1
                dur = (wf.updated_at - wf.created_at).total_seconds()
                durations.append(max(0.0, dur))
            elif status_val == WorkflowStatus.FAILED.value:
                failed += 1
                dur = (wf.updated_at - wf.created_at).total_seconds()
                durations.append(max(0.0, dur))
            elif status_val in (
                WorkflowStatus.PAUSED.value,
                WorkflowStatus.WAITING_FOR_APPROVAL.value,
            ):
                paused += 1

        avg_time = sum(durations) / len(durations) if durations else 0.0
        finished = completed + failed
        success_rate = (completed / finished * 100.0) if finished > 0 else 100.0

        return WorkflowMetricsSummary(
            total_workflows=total,
            running_workflows=running,
            completed_workflows=completed,
            failed_workflows=failed,
            paused_workflows=paused,
            average_execution_time_seconds=round(avg_time, 2),
            success_rate=round(success_rate, 2),
        )

    def get_agent_metrics(self) -> AgentMetricsSummary:
        """Compute aggregated agent execution metrics."""
        workflows = list(self._engine._workflows.values())

        executions: dict[str, int] = {}
        successes: dict[str, int] = {}
        failures: dict[str, int] = {}
        duration_sums: dict[str, float] = {}
        last_times: dict[str, str | None] = {}

        for wf in workflows:
            for step in wf.execution_steps:
                agent_id = step.agent_id or "unknown"
                executions[agent_id] = executions.get(agent_id, 0) + 1

                step_status = (
                    step.status.value
                    if hasattr(step.status, "value")
                    else str(step.status)
                )
                if step_status == WorkflowStatus.COMPLETED.value:
                    successes[agent_id] = successes.get(agent_id, 0) + 1
                elif step_status == WorkflowStatus.FAILED.value:
                    failures[agent_id] = failures.get(agent_id, 0) + 1

                if step.started_at and step.completed_at:
                    dur = (step.completed_at - step.started_at).total_seconds()
                    duration_sums[agent_id] = duration_sums.get(agent_id, 0.0) + max(
                        0.0, dur
                    )

                if step.completed_at:
                    iso_t = step.completed_at.isoformat()
                    if agent_id not in last_times or iso_t > (
                        last_times[agent_id] or ""
                    ):
                        last_times[agent_id] = iso_t

        avg_durations: dict[str, float] = {}
        for agent_id, total_exec in executions.items():
            sum_dur = duration_sums.get(agent_id, 0.0)
            avg_durations[agent_id] = (
                round(sum_dur / total_exec, 2) if total_exec else 0.0
            )
            if agent_id not in successes:
                successes[agent_id] = 0
            if agent_id not in failures:
                failures[agent_id] = 0

        return AgentMetricsSummary(
            executions_per_agent=executions,
            successful_executions=successes,
            failed_executions=failures,
            average_execution_duration_seconds=avg_durations,
            last_execution_time=last_times,
        )

    def get_workflow_details(self, workflow_id: str) -> WorkflowMonitoringDetails:
        """Retrieve runtime monitoring details for a specific workflow."""
        wf = self._engine.load_workflow(workflow_id)

        executed_agents: list[str] = []
        current_step_name: str | None = None
        history: list[dict[str, Any]] = []

        for step in wf.execution_steps:
            if step.agent_id and step.agent_id not in executed_agents:
                executed_agents.append(step.agent_id)

            step_status = (
                step.status.value if hasattr(step.status, "value") else str(step.status)
            )
            if step_status == WorkflowStatus.RUNNING.value:
                current_step_name = step.name

            history.append(
                {
                    "step_id": step.step_id,
                    "name": step.name,
                    "agent_id": step.agent_id,
                    "status": step_status,
                    "started_at": step.started_at.isoformat()
                    if step.started_at
                    else None,
                    "completed_at": step.completed_at.isoformat()
                    if step.completed_at
                    else None,
                    "error": step.error,
                }
            )

        end_t = wf.updated_at if wf.updated_at else datetime.now(UTC)
        duration = max(0.0, (end_t - wf.created_at).total_seconds())

        state_val = (
            wf.workflow_status.value
            if hasattr(wf.workflow_status, "value")
            else str(wf.workflow_status)
        )

        return WorkflowMonitoringDetails(
            workflow_id=wf.workflow_id,
            workflow_name=wf.workflow_name,
            current_state=state_val,
            current_step=current_step_name,
            executed_agents=executed_agents,
            execution_history=history,
            created_at=wf.created_at.isoformat(),
            updated_at=wf.updated_at.isoformat(),
            duration_seconds=round(duration, 2),
        )
