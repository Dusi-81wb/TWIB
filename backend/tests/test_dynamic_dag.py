"""Tests for Dynamic Multi-Agent DAG Planner, Dispatcher, and Execution Engine."""

import asyncio
import time
from typing import Any

import pytest

from app.agents.agent_dag import (
    AgentDAGPlan,
    AgentNode,
    DAGExecutionResult,
    NodeStatus,
)
from app.agents.base_agent import BaseAgent
from app.agents.dag_dispatcher import AsyncDAGDispatcher
from app.agents.dag_planner import DynamicDAGPlanner
from app.agents.exceptions import AgentValidationError
from app.agents.models import (
    AgentMetadata,
    AgentRequest,
    AgentResponse,
    AgentStatus,
)
from app.agents.supervisor_agent import SupervisorAgent
from app.workflows.workflow import Workflow
from app.workflows.workflow_executor import WorkflowExecutor
from app.workflows.workflow_models import WorkflowStatus


class MockTimedAgent(BaseAgent):
    """Mock agent that simulates execution work with delay."""

    def __init__(self, agent_id: str, delay_seconds: float = 0.05, fail_times: int = 0) -> None:
        super().__init__()
        self._agent_id = agent_id
        self._delay = delay_seconds
        self._fail_times = fail_times
        self._attempts = 0

    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            id=self._agent_id,
            name=f"Mock {self._agent_id}",
            description="Mock timed agent",
            version="1.0.0",
        )

    async def execute(self, request: AgentRequest) -> AgentResponse:
        self._attempts += 1
        if self._delay > 0:
            await asyncio.sleep(self._delay)

        if self._attempts <= self._fail_times:
            raise RuntimeError(f"Simulated failure in {self._agent_id} on attempt {self._attempts}")

        return AgentResponse(
            agent_id=self._agent_id,
            status=AgentStatus.COMPLETED,
            result={
                "agent": self._agent_id,
                "received_prompt": request.user_prompt,
                "received_deps": request.context.get("upstream_dependencies", {}),
            },
        )


# =====================================================================
# DAG Structure & Validation Tests
# =====================================================================

def test_dag_validation_valid_diamond() -> None:
    """A valid diamond DAG (A -> B, A -> C, B+C -> D) should pass and return 3 waves."""
    plan = AgentDAGPlan(
        goal="Design workflow",
        nodes=[
            AgentNode(node_id="node_a", agent_id="planner", dependencies=[]),
            AgentNode(node_id="node_b", agent_id="research", dependencies=["node_a"]),
            AgentNode(node_id="node_c", agent_id="analyst", dependencies=["node_a"]),
            AgentNode(node_id="node_d", agent_id="architect", dependencies=["node_b", "node_c"]),
        ],
    )
    waves = plan.validate_graph()
    assert len(waves) == 3
    assert waves[0] == ["node_a"]
    assert set(waves[1]) == {"node_b", "node_c"}
    assert waves[2] == ["node_d"]


def test_dag_validation_detects_cycles() -> None:
    """Cyclic dependencies (A -> B -> C -> A) must raise AgentValidationError."""
    plan = AgentDAGPlan(
        goal="Cyclic test",
        nodes=[
            AgentNode(node_id="a", agent_id="planner", dependencies=["c"]),
            AgentNode(node_id="b", agent_id="research", dependencies=["a"]),
            AgentNode(node_id="c", agent_id="analyst", dependencies=["b"]),
        ],
    )
    with pytest.raises(AgentValidationError) as exc:
        plan.validate_graph()
    assert "Cyclic dependency detected" in str(exc.value)


def test_dag_validation_detects_self_dependency() -> None:
    """Self-referencing node must raise AgentValidationError."""
    plan = AgentDAGPlan(
        goal="Self cycle test",
        nodes=[
            AgentNode(node_id="a", agent_id="planner", dependencies=["a"]),
        ],
    )
    with pytest.raises(AgentValidationError) as exc:
        plan.validate_graph()
    assert "cannot depend on itself" in str(exc.value)


def test_dag_validation_detects_missing_dependency() -> None:
    """Referencing a non-existent node ID must raise AgentValidationError."""
    plan = AgentDAGPlan(
        goal="Missing dep test",
        nodes=[
            AgentNode(node_id="a", agent_id="planner", dependencies=["non_existent_node"]),
        ],
    )
    with pytest.raises(AgentValidationError) as exc:
        plan.validate_graph()
    assert "depends on non-existent node" in str(exc.value)


# =====================================================================
# Dynamic DAG Planner Tests
# =====================================================================

@pytest.mark.asyncio
async def test_dynamic_dag_planner_heuristic_comprehensive() -> None:
    """Heuristic planner generates 5-stage comprehensive graph with parallel branches."""
    planner = DynamicDAGPlanner()
    plan = await planner.plan_dag(goal="Build a full automated invoice approval workflow")
    assert plan is not None
    assert len(plan.nodes) >= 6
    waves = plan.validate_graph()
    assert len(waves) >= 4

    # Check node IDs and dependencies
    node_ids = {n.node_id for n in plan.nodes}
    assert "step_planner" in node_ids
    assert "step_research" in node_ids
    assert "step_analyst" in node_ids
    assert "step_architect" in node_ids


@pytest.mark.asyncio
async def test_dynamic_dag_planner_targeted_subgraph() -> None:
    """Heuristic planner generates compact targeted subgraph for research tasks."""
    planner = DynamicDAGPlanner()
    plan = await planner.plan_dag(goal="Quick research on OAuth2 scopes")
    assert plan is not None
    assert len(plan.nodes) == 2
    assert plan.nodes[0].agent_id == "research"
    assert plan.nodes[1].agent_id == "documentation"


# =====================================================================
# Async DAG Dispatcher Concurrency & Resilience Tests
# =====================================================================

@pytest.mark.asyncio
async def test_dag_dispatcher_parallel_speedup() -> None:
    """Parallel branch execution (node_b and node_c) runs concurrently."""
    delay = 0.1
    registry = {
        "planner": MockTimedAgent("planner", delay_seconds=delay),
        "research": MockTimedAgent("research", delay_seconds=delay),
        "analyst": MockTimedAgent("analyst", delay_seconds=delay),
        "architect": MockTimedAgent("architect", delay_seconds=delay),
    }

    plan = AgentDAGPlan(
        goal="Concurrency test",
        nodes=[
            AgentNode(node_id="node_a", agent_id="planner", dependencies=[]),
            AgentNode(node_id="node_b", agent_id="research", dependencies=["node_a"]),
            AgentNode(node_id="node_c", agent_id="analyst", dependencies=["node_a"]),
            AgentNode(node_id="node_d", agent_id="architect", dependencies=["node_b", "node_c"]),
        ],
    )

    dispatcher = AsyncDAGDispatcher(agent_registry=registry)
    t0 = time.monotonic()
    result = await dispatcher.execute_plan(plan)
    elapsed = time.monotonic() - t0

    assert result.status == NodeStatus.COMPLETED
    assert len(result.node_results) == 4
    # Serial execution would be at least 4 * 0.1 = 0.4s.
    # Parallel execution with node_b + node_c in parallel should be ~ 3 * 0.1 = 0.3s.
    # We verify it finishes well below serial time plus buffer.
    assert elapsed < 0.38


@pytest.mark.asyncio
async def test_dag_dispatcher_retry_mechanism() -> None:
    """A node that fails on the first attempt succeeds on retry."""
    # fail 1 time, with max_retries = 2
    failing_agent = MockTimedAgent("research", delay_seconds=0.01, fail_times=1)
    registry = {
        "research": failing_agent,
    }

    plan = AgentDAGPlan(
        goal="Retry test",
        nodes=[
            AgentNode(
                node_id="node_r",
                agent_id="research",
                dependencies=[],
                max_retries=2,
                retry_delay_seconds=0.01,
            ),
        ],
    )

    dispatcher = AsyncDAGDispatcher(agent_registry=registry)
    result = await dispatcher.execute_plan(plan)

    assert result.status == NodeStatus.COMPLETED
    assert result.node_results["node_r"].status == NodeStatus.COMPLETED
    assert result.node_results["node_r"].retry_attempts == 1


@pytest.mark.asyncio
async def test_dag_dispatcher_optional_failure_isolation() -> None:
    """Failure in an optional node allows the rest of the DAG to complete."""
    registry = {
        "planner": MockTimedAgent("planner", delay_seconds=0.01),
        "research": MockTimedAgent("research", delay_seconds=0.01, fail_times=99),  # fails
        "analyst": MockTimedAgent("analyst", delay_seconds=0.01),
        "architect": MockTimedAgent("architect", delay_seconds=0.01),
    }

    plan = AgentDAGPlan(
        goal="Optional failure test",
        nodes=[
            AgentNode(node_id="node_p", agent_id="planner", dependencies=[]),
            AgentNode(node_id="node_r", agent_id="research", dependencies=["node_p"], optional=True, max_retries=0),
            AgentNode(node_id="node_a", agent_id="analyst", dependencies=["node_p"]),
            AgentNode(node_id="node_arch", agent_id="architect", dependencies=["node_r", "node_a"]),
        ],
    )

    dispatcher = AsyncDAGDispatcher(agent_registry=registry)
    result = await dispatcher.execute_plan(plan)

    assert result.status == NodeStatus.COMPLETED
    assert result.node_results["node_r"].status == NodeStatus.FAILED
    assert result.node_results["node_a"].status == NodeStatus.COMPLETED
    assert result.node_results["node_arch"].status == NodeStatus.COMPLETED


@pytest.mark.asyncio
async def test_dag_dispatcher_required_failure_skips_downstream() -> None:
    """Failure in a required non-optional node skips downstream dependencies."""
    registry = {
        "planner": MockTimedAgent("planner", delay_seconds=0.01, fail_times=99),  # fails
        "research": MockTimedAgent("research", delay_seconds=0.01),
    }

    plan = AgentDAGPlan(
        goal="Required failure test",
        nodes=[
            AgentNode(node_id="node_p", agent_id="planner", dependencies=[], optional=False, max_retries=0),
            AgentNode(node_id="node_r", agent_id="research", dependencies=["node_p"]),
        ],
    )

    dispatcher = AsyncDAGDispatcher(agent_registry=registry)
    result = await dispatcher.execute_plan(plan)

    assert result.status == NodeStatus.FAILED
    assert result.node_results["node_p"].status == NodeStatus.FAILED
    assert result.node_results["node_r"].status == NodeStatus.SKIPPED


# =====================================================================
# End-to-End Supervisor & Workflow Integration Tests
# =====================================================================

@pytest.mark.asyncio
async def test_supervisor_dynamic_dag_execution() -> None:
    """SupervisorAgent properly executes in dynamic DAG mode and outputs structured DAG metadata."""
    registry = {
        "planner": MockTimedAgent("planner", delay_seconds=0.01),
        "research": MockTimedAgent("research", delay_seconds=0.01),
        "analyst": MockTimedAgent("analyst", delay_seconds=0.01),
        "architect": MockTimedAgent("architect", delay_seconds=0.01),
        "validator": MockTimedAgent("validator", delay_seconds=0.01),
        "optimizer": MockTimedAgent("optimizer", delay_seconds=0.01),
        "documentation": MockTimedAgent("documentation", delay_seconds=0.01),
    }

    supervisor = SupervisorAgent(agent_registry=registry)
    req = AgentRequest(
        agent_id="supervisor",
        user_prompt="Build multi-tenant invoice approval workflow",
        context={"dynamic_routing": True},
    )

    res = await supervisor.execute(req)
    assert res.status == AgentStatus.COMPLETED
    assert res.result is not None
    assert "dag_plan" in res.result
    assert "execution_graph" in res.result
    assert len(res.result["executed_steps"]) > 0


@pytest.mark.asyncio
async def test_workflow_executor_integrates_dag() -> None:
    """WorkflowExecutor running a DAG workflow persists DAG plan and graph in metadata."""
    registry = {
        "planner": MockTimedAgent("planner", delay_seconds=0.01),
        "research": MockTimedAgent("research", delay_seconds=0.01),
        "analyst": MockTimedAgent("analyst", delay_seconds=0.01),
        "architect": MockTimedAgent("architect", delay_seconds=0.01),
        "validator": MockTimedAgent("validator", delay_seconds=0.01),
        "optimizer": MockTimedAgent("optimizer", delay_seconds=0.01),
        "documentation": MockTimedAgent("documentation", delay_seconds=0.01),
    }

    supervisor = SupervisorAgent(agent_registry=registry)
    executor = WorkflowExecutor(supervisor_agent=supervisor)

    wf = Workflow(
        workflow_name="Dynamic DAG Approval Workflow",
        user_request="Design payment workflow",
        metadata={"context": {"dynamic_routing": True}},
    )

    executed_wf = await executor.execute(wf)
    assert executed_wf.workflow_status == WorkflowStatus.COMPLETED
    assert "dag_plan" in executed_wf.metadata
    assert "execution_graph" in executed_wf.metadata
    assert len(executed_wf.execution_steps) > 0
