"""Async DAG Dispatcher for Multi-Agent Workflows.

Orchestrates concurrent, wave-based topological execution of agent nodes,
handles retry backoffs, context merging, failure isolation, and real-time progress events.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
import inspect
import logging
import time
from typing import Any, Callable

from app.agents.agent_dag import (
    AgentDAGPlan,
    AgentNode,
    DAGExecutionResult,
    NodeExecutionRecord,
    NodeStatus,
)
from app.agents.base_agent import BaseAgent
from app.agents.models import AgentRequest, AgentResponse, AgentStatus

logger = logging.getLogger(__name__)


class AsyncDAGDispatcher:
    """Dispatches and orchestrates dynamic multi-agent DAG execution."""

    def __init__(
        self,
        agent_registry: dict[str, BaseAgent],
        event_hook: Callable[[str, dict[str, Any]], Any] | None = None,
    ) -> None:
        """Initialize AsyncDAGDispatcher.

        Args:
            agent_registry: Mapping of agent_id -> BaseAgent instances.
            event_hook: Optional sync or async callback for dispatch events (event_name, payload).
        """
        self._agents = agent_registry
        self._event_hook = event_hook

    async def _emit_event(self, event_name: str, payload: dict[str, Any]) -> None:
        """Safely emit an event to the registered hook."""
        if not self._event_hook:
            return
        try:
            res = self._event_hook(event_name, payload)
            if inspect.isawaitable(res):
                await res
        except Exception as exc:
            logger.debug("Error in DAG dispatch event hook: %s", exc)

    async def execute_plan(
        self,
        plan: AgentDAGPlan,
        context: dict[str, Any] | None = None,
        provider: str | None = None,
        model: str | None = None,
    ) -> DAGExecutionResult:
        """Execute a validated multi-agent DAG plan.

        Dispatches independent nodes concurrently in topological waves,
        passing upstream results as context to downstream nodes.

        Args:
            plan: The AgentDAGPlan to execute.
            context: Base workflow or request context.
            provider: Optional default LLM provider.
            model: Optional default model name.

        Returns:
            Aggregated DAGExecutionResult detailing all node outputs and durations.
        """
        waves = plan.validate_graph()
        base_ctx = dict(context or {})

        start_time = time.monotonic()
        records: dict[str, NodeExecutionRecord] = {
            node.node_id: NodeExecutionRecord(
                node_id=node.node_id,
                agent_id=node.agent_id,
                status=NodeStatus.PENDING,
            )
            for node in plan.nodes
        }
        node_outputs: dict[str, Any] = {}
        adjacency: dict[str, list[str]] = {node.node_id: [] for node in plan.nodes}
        for node in plan.nodes:
            for dep in node.dependencies:
                if dep in adjacency:
                    adjacency[dep].append(node.node_id)

        await self._emit_event(
            "dag.started",
            {
                "plan_id": plan.plan_id,
                "goal": plan.goal,
                "total_nodes": len(plan.nodes),
                "waves_count": len(waves),
            },
        )

        overall_status = NodeStatus.COMPLETED

        # Execute wave by wave; all nodes within a wave run concurrently
        for wave_idx, wave_nodes in enumerate(waves):
            # Check if any nodes in this wave have failed required dependencies
            nodes_to_run: list[AgentNode] = []
            for node_id in wave_nodes:
                node = plan.get_node(node_id)
                if not node:
                    continue

                # Verify all upstream dependencies succeeded
                dep_failed = False
                for dep_id in node.dependencies:
                    dep_rec = records.get(dep_id)
                    dep_node = plan.get_node(dep_id)
                    # If dependency failed and was not optional, skip this node
                    if dep_rec and dep_rec.status == NodeStatus.FAILED:
                        if dep_node and not dep_node.optional:
                            dep_failed = True
                            break
                    elif dep_rec and dep_rec.status == NodeStatus.SKIPPED:
                        dep_failed = True
                        break

                if dep_failed:
                    records[node_id].status = NodeStatus.SKIPPED
                    records[node_id].error = "Skipped due to upstream dependency failure"
                    await self._emit_event(
                        "node.skipped",
                        {"plan_id": plan.plan_id, "node_id": node_id, "reason": records[node_id].error},
                    )
                else:
                    nodes_to_run.append(node)

            if not nodes_to_run:
                continue

            # Run all independent nodes in this wave concurrently
            tasks = [
                self._execute_node(
                    node=node,
                    plan=plan,
                    base_context=base_ctx,
                    upstream_outputs=node_outputs,
                    provider=provider,
                    model=model,
                )
                for node in nodes_to_run
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for node, res in zip(nodes_to_run, results):
                if isinstance(res, Exception):
                    records[node.node_id].status = NodeStatus.FAILED
                    records[node.node_id].error = str(res)
                    if not node.optional:
                        overall_status = NodeStatus.FAILED
                else:
                    rec, output = res
                    records[node.node_id] = rec
                    if rec.status == NodeStatus.COMPLETED:
                        node_outputs[node.node_id] = output
                    elif rec.status == NodeStatus.FAILED and not node.optional:
                        overall_status = NodeStatus.FAILED

        total_duration = round(time.monotonic() - start_time, 3)

        # Determine terminal node result as final_result
        final_result = None
        if waves and waves[-1]:
            last_wave_completed = [
                node_outputs[nid]
                for nid in waves[-1]
                if nid in node_outputs
            ]
            if len(last_wave_completed) == 1:
                final_result = last_wave_completed[0]
            elif last_wave_completed:
                final_result = last_wave_completed

        completed_count = sum(1 for r in records.values() if r.status == NodeStatus.COMPLETED)
        summary = (
            f"Dynamic DAG execution {overall_status.value} in {total_duration}s. "
            f"Completed {completed_count}/{len(plan.nodes)} nodes across {len(waves)} waves."
        )

        result_obj = DAGExecutionResult(
            plan_id=plan.plan_id,
            goal=plan.goal,
            status=overall_status,
            node_results=records,
            final_result=final_result,
            summary=summary,
            total_duration_seconds=total_duration,
            execution_graph=adjacency,
        )

        await self._emit_event(
            "dag.completed",
            {
                "plan_id": plan.plan_id,
                "status": overall_status.value,
                "duration": total_duration,
                "summary": summary,
            },
        )

        return result_obj

    async def _execute_node(
        self,
        node: AgentNode,
        plan: AgentDAGPlan,
        base_context: dict[str, Any],
        upstream_outputs: dict[str, Any],
        provider: str | None,
        model: str | None,
    ) -> tuple[NodeExecutionRecord, Any]:
        """Execute a single agent node with retries and timing."""
        rec = NodeExecutionRecord(
            node_id=node.node_id,
            agent_id=node.agent_id,
            status=NodeStatus.RUNNING,
            started_at=datetime.now(UTC).isoformat(),
        )

        await self._emit_event(
            "node.started",
            {
                "plan_id": plan.plan_id,
                "node_id": node.node_id,
                "agent_id": node.agent_id,
                "name": node.name,
            },
        )

        node_start = time.monotonic()

        if node.agent_id not in self._agents:
            rec.status = NodeStatus.FAILED
            rec.error = f"Agent '{node.agent_id}' not found in registry"
            rec.duration_seconds = round(time.monotonic() - node_start, 3)
            rec.completed_at = datetime.now(UTC).isoformat()
            await self._emit_event(
                "node.failed",
                {
                    "plan_id": plan.plan_id,
                    "node_id": node.node_id,
                    "error": rec.error,
                },
            )
            return rec, None

        agent = self._agents[node.agent_id]

        # Assemble contextual payload
        node_ctx = dict(base_context)
        # Collect outputs from specified prerequisite dependencies
        deps_data = {dep_id: upstream_outputs.get(dep_id) for dep_id in node.dependencies if dep_id in upstream_outputs}
        node_ctx["upstream_dependencies"] = deps_data
        node_ctx["node_id"] = node.node_id
        node_ctx["node_name"] = node.name

        prompt_to_use = node.input_prompt_override or plan.goal

        agent_req = AgentRequest(
            agent_id=node.agent_id,
            user_prompt=prompt_to_use,
            context=node_ctx,
            provider=provider,
            model=model,
        )

        attempts = 0
        last_error: str | None = None
        output_result: Any = None

        while attempts <= node.max_retries:
            attempts += 1
            rec.retry_attempts = attempts - 1
            try:
                agent_res: AgentResponse = await agent.execute(agent_req)
                if agent_res.status == AgentStatus.COMPLETED:
                    rec.status = NodeStatus.COMPLETED
                    rec.result = agent_res.result
                    output_result = agent_res.result
                    break
                else:
                    last_error = f"Agent returned status {agent_res.status}"
            except Exception as exc:
                last_error = str(exc)
                logger.warning(
                    "Node '%s' execution attempt %d failed: %s",
                    node.node_id,
                    attempts,
                    exc,
                )

            if attempts <= node.max_retries and node.retry_delay_seconds > 0:
                await asyncio.sleep(node.retry_delay_seconds * (2 ** (attempts - 1)))

        rec.duration_seconds = round(time.monotonic() - node_start, 3)
        rec.completed_at = datetime.now(UTC).isoformat()

        if rec.status != NodeStatus.COMPLETED:
            rec.status = NodeStatus.FAILED
            rec.error = last_error or "Execution failed"
            await self._emit_event(
                "node.failed",
                {
                    "plan_id": plan.plan_id,
                    "node_id": node.node_id,
                    "error": rec.error,
                    "duration": rec.duration_seconds,
                },
            )
        else:
            await self._emit_event(
                "node.completed",
                {
                    "plan_id": plan.plan_id,
                    "node_id": node.node_id,
                    "duration": rec.duration_seconds,
                },
            )

        return rec, output_result
