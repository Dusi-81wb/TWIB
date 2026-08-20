"""Workflow Executor Core implementation.

Provides production-ready execution of Directed Acyclic Graphs (DAGs) with:
- Topological parallel wave dispatching via asyncio.gather
- Node input/output data propagation ($nodes.<id>.<key> and $context.<key>)
- Conditional branching and dynamic path routing
- Configurable retry policies with exponential backoff and jitter
- Checkpointing and resumption recovery from saved state snapshots
- Human-in-the-loop approval pause/resume handling
- Graceful failure propagation and task cancellation
- Real-time telemetry event hooks
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from datetime import UTC, datetime
import random
import time
from typing import Any
import uuid

from app.agents.models import AgentRequest, AgentStatus
from app.agents.supervisor_agent import SupervisorAgent
from app.domain.workflows.entities import (
    Workflow,
    WorkflowCheckpoint,
    WorkflowExecution,
)
from app.domain.workflows.exceptions import (
    NodeExecutionError,
    WorkflowExecutionError,
    WorkflowNotFoundError,
    WorkflowStateError,
    WorkflowValidationError,
)
from app.domain.workflows.value_objects import (
    ApprovalStatus,
    CheckpointType,
    EdgeType,
    NodeExecutionState,
    NodeStatus,
    WorkflowStatus,
)
from app.workflows.workflow_models import WorkflowStep

from app.workflows.nodes.base_node import BaseWorkflowNode
from app.workflows.nodes.node_types import ConditionNode, HumanNode
from app.workflows.workflow_engine import WorkflowEngine
from app.workflows.workflow_graph import WorkflowGraph


class WorkflowExecutionResult:
    """Structured execution report returned by the WorkflowExecutor."""

    def __init__(
        self,
        execution_id: str,
        workflow_id: str,
        status: WorkflowStatus,
        node_states: dict[str, NodeExecutionState],
        step_outputs: dict[str, Any],
        duration_seconds: float = 0.0,
        error: str | None = None,
        checkpoint_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.execution_id = execution_id
        self.workflow_id = workflow_id
        self.status = status
        self.node_states = node_states
        self.step_outputs = step_outputs
        self.duration_seconds = duration_seconds
        self.error = error
        self.checkpoint_id = checkpoint_id
        self.metadata = metadata or {}

    def to_dict(self) -> dict[str, Any]:
        """Serialize execution result to dictionary."""
        return {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "status": str(self.status.value if hasattr(self.status, "value") else self.status),
            "node_states": {nid: s.to_dict() for nid, s in self.node_states.items()},
            "step_outputs": self.step_outputs,
            "duration_seconds": self.duration_seconds,
            "error": self.error,
            "checkpoint_id": self.checkpoint_id,
            "metadata": self.metadata,
        }


class WorkflowExecutor:
    """Production DAG Workflow Executor supporting parallel waves, retries, checkpointing, and recovery."""

    def __init__(
        self,
        engine: WorkflowEngine | None = None,
        supervisor_agent: SupervisorAgent | None = None,
        event_listener: Callable[[str, dict[str, Any]], None] | None = None,
    ) -> None:
        self._engine = engine or WorkflowEngine(supervisor_agent=supervisor_agent)
        self._supervisor = supervisor_agent or self._engine.supervisor
        self._event_listener = event_listener
        self._cancelled_executions: set[str] = set()

    @property
    def engine(self) -> WorkflowEngine:
        return self._engine

    @property
    def supervisor(self) -> SupervisorAgent:
        return self._supervisor

    # =========================================================================
    # High-level Workflow Execution Entry Points
    # =========================================================================

    async def execute(
        self,
        workflow_or_id: Any,
        context: dict[str, Any] | None = None,
    ) -> Any:
        """Execute a workflow entity or workflow_id.

        If the workflow contains a DAG definition in its graph_definition or metadata,
        it is executed using the full DAG engine. Otherwise it falls back to the supervisor pipeline.
        """
        workflow = self._resolve_workflow(workflow_or_id)

        # Check if workflow has a structured DAG graph
        graph_def = getattr(workflow, "graph_definition", None)
        if not graph_def and isinstance(getattr(workflow, "metadata", None), dict):
            graph_def = workflow.metadata.get("graph_definition") or workflow.metadata.get("dag_plan")

        if graph_def and (graph_def.get("nodes") or graph_def.get("edges")):
            graph = WorkflowGraph.from_dict(graph_def)
            merged_ctx = {
                "workflow_id": workflow.workflow_id,
                "user_request": getattr(workflow, "user_request", ""),
                **(getattr(workflow, "metadata", {}).get("context", {})),
                **(context or {}),
            }
            exec_res = await self.execute_graph(
                graph=graph,
                initial_context=merged_ctx,
                workflow_id=workflow.workflow_id,
            )

            # Update legacy Workflow step records for compatibility
            steps: list[WorkflowStep] = []
            for nid, nstate in exec_res.node_states.items():
                node_obj = graph.get_node(nid) if graph.has_node(nid) else None
                agent_id = getattr(node_obj, "agent_id", None) if node_obj else None
                wf_status = WorkflowStatus.COMPLETED if nstate.status == NodeStatus.COMPLETED else (
                    WorkflowStatus.FAILED if nstate.status == NodeStatus.FAILED else WorkflowStatus.RUNNING
                )
                step = WorkflowStep(
                    step_id=nid,
                    name=getattr(node_obj, "name", f"Node {nid}"),
                    agent_id=agent_id,
                    status=wf_status,
                    input_data=nstate.inputs,
                    output_data=nstate.outputs,
                    error=nstate.error,
                    started_at=nstate.started_at,
                    completed_at=nstate.completed_at,
                )
                steps.append(step)

            if hasattr(workflow, "execution_steps"):
                workflow.execution_steps = steps

            if exec_res.status == WorkflowStatus.COMPLETED:
                workflow.mark_completed()
            elif exec_res.status == WorkflowStatus.WAITING_FOR_APPROVAL:
                workflow.update_status(WorkflowStatus.WAITING_FOR_APPROVAL)
            elif exec_res.status == WorkflowStatus.FAILED:
                workflow.mark_failed(exec_res.error or "Workflow DAG execution failed")

            return workflow

        # Fallback to Supervisor Agent pipeline
        self._engine.validate_workflow(workflow)
        workflow.mark_running()
        self._emit_event("workflow.started", {"workflow_id": workflow.workflow_id})

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
            self._emit_event("workflow.failed", {"workflow_id": workflow.workflow_id, "error": err_msg})
            raise WorkflowExecutionError(err_msg, workflow_id=workflow.workflow_id) from err

        sup_dict = sup_res.result or {}
        executed_steps = sup_dict.get("executed_steps", [])

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
        workflow.metadata["total_duration_seconds"] = sup_dict.get("total_duration_seconds")
        if "dag_plan" in sup_dict:
            workflow.metadata["dag_plan"] = sup_dict["dag_plan"]
        if "execution_graph" in sup_dict:
            workflow.metadata["execution_graph"] = sup_dict["execution_graph"]

        if sup_res.status == AgentStatus.COMPLETED:
            workflow.mark_completed()
            self._emit_event("workflow.completed", {"workflow_id": workflow.workflow_id, "result": sup_dict.get("final_result")})
        else:
            failure_reason = sup_res.error or "Supervisor execution reported step failures."
            workflow.mark_failed(failure_reason)
            self._emit_event("workflow.failed", {"workflow_id": workflow.workflow_id, "error": failure_reason})

        return workflow

    # =========================================================================
    # Full DAG Execution Engine
    # =========================================================================

    async def execute_graph(
        self,
        graph: WorkflowGraph,
        initial_context: dict[str, Any] | None = None,
        execution_id: str | None = None,
        workflow_id: str | None = None,
        node_states_override: dict[str, NodeExecutionState] | None = None,
        step_outputs_override: dict[str, Any] | None = None,
    ) -> WorkflowExecutionResult:
        """Execute a complete WorkflowGraph DAG with wave parallelism, data passing, retries, and checkpointing."""
        # 1. Validate graph structure
        graph.validate()

        wid = workflow_id or str(uuid.uuid4())
        eid = execution_id or str(uuid.uuid4())
        context = dict(initial_context or {})
        start_time = time.perf_counter()

        node_states: dict[str, NodeExecutionState] = node_states_override or {
            nid: NodeExecutionState(node_id=nid, max_retries=graph.get_node(nid).max_retries)
            for nid in graph.nodes
        }
        step_outputs: dict[str, Any] = step_outputs_override or {}
        skipped_nodes: set[str] = set()

        self._emit_event("workflow.started", {"workflow_id": wid, "execution_id": eid})

        # Calculate parallel execution waves
        waves = graph.get_execution_waves()

        for wave_idx, wave_nodes in enumerate(waves):
            if eid in self._cancelled_executions:
                self._emit_event("workflow.cancelled", {"workflow_id": wid, "execution_id": eid})
                return WorkflowExecutionResult(
                    execution_id=eid,
                    workflow_id=wid,
                    status=WorkflowStatus.CANCELLED,
                    node_states=node_states,
                    step_outputs=step_outputs,
                    duration_seconds=time.perf_counter() - start_time,
                    error="Execution cancelled by user",
                )

            # Filter ready nodes in this wave
            nodes_to_execute: list[BaseWorkflowNode] = []
            for nid in wave_nodes:
                node = graph.get_node(nid)
                state = node_states[nid]

                # If node already completed in a restored checkpoint, skip re-execution
                if state.status == NodeStatus.COMPLETED:
                    continue

                if nid in skipped_nodes:
                    state.mark_skipped(reason="Branch condition not satisfied")
                    self._emit_event("node.skipped", {"workflow_id": wid, "execution_id": eid, "node_id": nid, "reason": state.error})
                    continue

                # Check prerequisite dependencies
                deps = graph.get_dependencies(nid)
                any_dep_failed = any(node_states[d].status == NodeStatus.FAILED for d in deps if not graph.get_node(d).optional)
                any_dep_skipped = any(d in skipped_nodes or node_states[d].status == NodeStatus.SKIPPED for d in deps)

                if any_dep_failed or any_dep_skipped:
                    state.mark_skipped(reason="Prerequisite node failed or skipped")
                    skipped_nodes.add(nid)
                    self._emit_event("node.skipped", {"workflow_id": wid, "execution_id": eid, "node_id": nid, "reason": state.error})
                    continue


                nodes_to_execute.append(node)

            if not nodes_to_execute:
                continue

            # Execute all ready nodes in parallel wave
            wave_tasks = [
                self._execute_single_node(
                    node=node,
                    state=node_states[node.node_id],
                    context=context,
                    step_outputs=step_outputs,
                    workflow_id=wid,
                    execution_id=eid,
                )
                for node in nodes_to_execute
            ]

            results = await asyncio.gather(*wave_tasks, return_exceptions=True)

            # Evaluate wave results and branch activations
            for node, res in zip(nodes_to_execute, results, strict=False):
                nid = node.node_id
                state = node_states[nid]

                if isinstance(res, Exception):
                    err_msg = str(res)
                    state.mark_failed(err_msg)
                    self._emit_event("node.failed", {"workflow_id": wid, "execution_id": eid, "node_id": nid, "error": err_msg})
                    if not node.optional:
                        # Fatal failure halts execution
                        duration = time.perf_counter() - start_time
                        self._emit_event("workflow.failed", {"workflow_id": wid, "execution_id": eid, "error": err_msg, "failed_node_id": nid})
                        return WorkflowExecutionResult(
                            execution_id=eid,
                            workflow_id=wid,
                            status=WorkflowStatus.FAILED,
                            node_states=node_states,
                            step_outputs=step_outputs,
                            duration_seconds=duration,
                            error=err_msg,
                        )
                else:
                    # Successful node output
                    step_outputs[nid] = res
                    # Handle ConditionNode branching
                    if isinstance(node, ConditionNode):
                        decision = res.get("decision", True)
                        for edge in graph.get_outgoing_edges(nid):
                            # If edge condition matches branch or if edge condition expression is evaluated
                            if edge.condition_expression:
                                if edge.condition_expression.lower() in ("true", "yes") and not decision:
                                    skipped_nodes.add(edge.target_node_id)
                                elif edge.condition_expression.lower() in ("false", "no") and decision:
                                    skipped_nodes.add(edge.target_node_id)
                            elif node.true_branch_target and not decision and edge.target_node_id == node.true_branch_target:
                                skipped_nodes.add(edge.target_node_id)
                            elif node.false_branch_target and decision and edge.target_node_id == node.false_branch_target:
                                skipped_nodes.add(edge.target_node_id)

                    # Handle HumanNode review checkpoint
                    if isinstance(node, HumanNode):
                        chk_id = str(uuid.uuid4())
                        duration = time.perf_counter() - start_time
                        state.mark_waiting_approval()
                        self._emit_event(
                            "workflow.paused",
                            {
                                "workflow_id": wid,
                                "execution_id": eid,
                                "node_id": nid,
                                "checkpoint_id": chk_id,
                                "title": node.title,
                            },
                        )
                        return WorkflowExecutionResult(
                            execution_id=eid,
                            workflow_id=wid,
                            status=WorkflowStatus.WAITING_FOR_APPROVAL,
                            node_states=node_states,
                            step_outputs=step_outputs,
                            duration_seconds=duration,
                            checkpoint_id=chk_id,
                            metadata={"paused_at_node": nid, "checkpoint_title": node.title},
                        )

        duration = time.perf_counter() - start_time
        self._emit_event("workflow.completed", {"workflow_id": wid, "execution_id": eid, "duration": duration})
        return WorkflowExecutionResult(
            execution_id=eid,
            workflow_id=wid,
            status=WorkflowStatus.COMPLETED,
            node_states=node_states,
            step_outputs=step_outputs,
            duration_seconds=duration,
        )

    # =========================================================================
    # Node Execution with Retry Policy
    # =========================================================================

    async def _execute_single_node(
        self,
        node: BaseWorkflowNode,
        state: NodeExecutionState,
        context: dict[str, Any],
        step_outputs: dict[str, Any],
        workflow_id: str,
        execution_id: str,
    ) -> dict[str, Any]:
        """Execute a single node with input resolution, retry backoff, and timeouts."""
        resolved_inputs = node.resolve_inputs(context_data=context, node_outputs=step_outputs)
        state.inputs = resolved_inputs

        attempt = 0
        max_attempts = 1 + node.max_retries

        while attempt < max_attempts:
            attempt += 1
            state.mark_running()
            self._emit_event(
                "node.started",
                {
                    "workflow_id": workflow_id,
                    "execution_id": execution_id,
                    "node_id": node.node_id,
                    "node_type": node.node_type,
                    "attempt": attempt,
                },
            )

            try:
                if node.timeout_seconds and node.timeout_seconds > 0:
                    out = await asyncio.wait_for(
                        node.execute(inputs=resolved_inputs, context=context),
                        timeout=node.timeout_seconds,
                    )
                else:
                    out = await node.execute(inputs=resolved_inputs, context=context)

                state.mark_completed(out)
                self._emit_event(
                    "node.completed",
                    {
                        "workflow_id": workflow_id,
                        "execution_id": execution_id,
                        "node_id": node.node_id,
                        "node_type": node.node_type,
                        "duration": state.duration_seconds,
                    },
                )
                return out

            except Exception as exc:
                err_msg = str(exc)
                is_retryable = not isinstance(exc, (WorkflowValidationError, PermissionError))

                if attempt < max_attempts and is_retryable:
                    # Exponential backoff with jitter
                    backoff = node.retry_delay_seconds * (2 ** (attempt - 1)) + random.uniform(0, 0.1)
                    state.mark_retrying(err_msg)
                    self._emit_event(
                        "node.retrying",
                        {
                            "workflow_id": workflow_id,
                            "execution_id": execution_id,
                            "node_id": node.node_id,
                            "attempt": attempt,
                            "max_retries": node.max_retries,
                            "delay_seconds": backoff,
                            "error": err_msg,
                        },
                    )
                    await asyncio.sleep(backoff)
                else:
                    state.mark_failed(err_msg)
                    raise

        raise NodeExecutionError(
            f"Node '{node.node_id}' failed after {max_attempts} attempts",
            node_id=node.node_id,
        )

    # =========================================================================
    # Checkpointing & Recovery
    # =========================================================================

    async def recover_execution(
        self,
        checkpoint: WorkflowCheckpoint | dict[str, Any],
        graph: WorkflowGraph,
        initial_context: dict[str, Any] | None = None,
    ) -> WorkflowExecutionResult:
        """Resume execution from a checkpoint snapshot, preserving completed node outputs and executing remaining tasks."""
        if isinstance(checkpoint, dict):
            state_snapshot = checkpoint.get("state_snapshot", {})
            workflow_id = checkpoint.get("workflow_id", str(uuid.uuid4()))
            execution_id = checkpoint.get("execution_id", str(uuid.uuid4()))
        else:
            state_snapshot = checkpoint.state_snapshot
            workflow_id = checkpoint.workflow_id
            execution_id = checkpoint.execution_id

        # Restore node states and step outputs
        node_states: dict[str, NodeExecutionState] = {}
        for nid, raw_s in state_snapshot.get("node_states", {}).items():
            node_states[nid] = NodeExecutionState.from_dict(raw_s)

        # Initialize any nodes not present in snapshot
        for nid in graph.nodes:
            if nid not in node_states:
                node_states[nid] = NodeExecutionState(node_id=nid, max_retries=graph.get_node(nid).max_retries)

        step_outputs = dict(state_snapshot.get("step_outputs", {}))
        restored_context = {**state_snapshot.get("context", {}), **(initial_context or {})}

        self._emit_event("workflow.resumed", {"workflow_id": workflow_id, "execution_id": execution_id})

        return await self.execute_graph(
            graph=graph,
            initial_context=restored_context,
            execution_id=execution_id,
            workflow_id=workflow_id,
            node_states_override=node_states,
            step_outputs_override=step_outputs,
        )

    def cancel_execution(self, execution_id: str) -> None:
        """Signal cancellation for an active execution ID."""
        self._cancelled_executions.add(execution_id)

    # =========================================================================
    # Step & Lifecycle Control Methods (Backwards Compatibility)
    # =========================================================================

    async def execute_step(
        self,
        workflow_or_id: Any,
        step_id: str,
    ) -> Any:
        """Execute a specific single step within a workflow."""
        workflow = self._resolve_workflow(workflow_or_id)
        target_step = next(
            (s for s in workflow.execution_steps if s.step_id == step_id or s.agent_id == step_id),
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
        self._emit_event("workflow.step.started", {"step_id": step_id, "workflow_id": workflow.workflow_id})

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
                self._emit_event("workflow.step.completed", {"step_id": step_id, "workflow_id": workflow.workflow_id})
            else:
                target_step.status = WorkflowStatus.FAILED
                target_step.error = sup_res.error or "Step execution failed."
                target_step.completed_at = datetime.now(UTC)
                workflow.mark_failed(target_step.error)
                self._emit_event("workflow.step.failed", {"step_id": step_id, "error": target_step.error})
        except Exception as err:
            err_msg = f"Step '{step_id}' execution failed: {err}"
            target_step.status = WorkflowStatus.FAILED
            target_step.error = err_msg
            target_step.completed_at = datetime.now(UTC)
            workflow.mark_failed(err_msg)
            raise WorkflowExecutionError(err_msg, workflow_id=workflow.workflow_id) from err

        return workflow

    def stop_execution(self, workflow_or_id: Any) -> Any:
        """Stop/cancel an in-flight workflow execution."""
        workflow = self._resolve_workflow(workflow_or_id)
        workflow.mark_cancelled()
        self._emit_event("workflow.cancelled", {"workflow_id": workflow.workflow_id})
        return workflow

    def pause_execution(self, workflow_or_id: Any) -> Any:
        """Pause an in-flight workflow execution."""
        workflow = self._resolve_workflow(workflow_or_id)
        workflow.mark_paused()
        self._emit_event("workflow.paused", {"workflow_id": workflow.workflow_id})
        return workflow

    async def resume_execution(self, workflow_or_id: Any) -> Any:
        """Resume execution of a paused workflow."""
        workflow = self._resolve_workflow(workflow_or_id)
        if workflow.workflow_status != WorkflowStatus.PAUSED and workflow.workflow_status != WorkflowStatus.WAITING_FOR_APPROVAL:
            err_msg = f"Cannot resume workflow in status '{workflow.workflow_status}'; must be PAUSED or WAITING_FOR_APPROVAL"
            raise WorkflowStateError(err_msg, workflow_id=workflow.workflow_id)
        self._emit_event("workflow.resumed", {"workflow_id": workflow.workflow_id})
        return await self.execute(workflow)

    def _resolve_workflow(self, workflow_or_id: Any) -> Any:
        if isinstance(workflow_or_id, (Workflow, str)):
            if isinstance(workflow_or_id, str):
                return self._engine.load_workflow(workflow_or_id)
            return workflow_or_id
        if hasattr(workflow_or_id, "workflow_id"):
            return workflow_or_id
        raise WorkflowValidationError("Invalid workflow reference provided")

    def _emit_event(self, event_type: str, payload: dict[str, Any]) -> None:
        if self._event_listener is not None:
            import contextlib
            with contextlib.suppress(Exception):
                self._event_listener(event_type, payload)
