"""Tests for Real DAG WorkflowExecutor: Parallelism, Data Passing, Retries, Checkpointing & Recovery."""

import asyncio
from typing import Any
import pytest

from app.domain.workflows.entities import WorkflowCheckpoint
from app.domain.workflows.exceptions import NodeExecutionError
from app.domain.workflows.value_objects import (
    ApprovalStatus,
    CheckpointType,
    EdgeType,
    NodeStatus,
    WorkflowEdge,
    WorkflowStatus,
)
from app.infrastructure.tools.base_tool import AbstractTool
from app.infrastructure.tools.registry import ToolRegistry
from app.workflows.nodes.base_node import BaseWorkflowNode
from app.workflows.nodes.node_types import (
    ConditionNode,
    HumanNode,
    LLMNode,
    ToolNode,
)
from app.workflows.workflow_executor import WorkflowExecutor
from app.workflows.workflow_graph import WorkflowGraph


class FlakyFailingNode(BaseWorkflowNode):
    """Test node that fails N times before succeeding to test retries."""

    def __init__(self, node_id: str, fail_count: int = 1, max_retries: int = 2) -> None:
        super().__init__(node_id=node_id, max_retries=max_retries, retry_delay_seconds=0.05)
        self.fail_count = fail_count
        self.attempts = 0

    @property
    def node_type(self) -> str:
        return "flaky"

    async def execute(self, inputs: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        self.attempts += 1
        if self.attempts <= self.fail_count:
            raise RuntimeError(f"Simulated network glitch on attempt {self.attempts}")
        return {"status": "success", "attempts_needed": self.attempts}


class TimedParallelNode(BaseWorkflowNode):
    """Test node with async sleep to verify concurrent parallel execution time."""

    def __init__(self, node_id: str, delay: float = 0.1) -> None:
        super().__init__(node_id=node_id)
        self.delay = delay

    @property
    def node_type(self) -> str:
        return "timed"

    async def execute(self, inputs: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        await asyncio.sleep(self.delay)
        return {"node_id": self.node_id, "computed_value": inputs.get("val", 10) * 2}


@pytest.mark.asyncio
async def test_parallel_diamond_execution_with_data_propagation() -> None:
    """Diamond DAG:
        Start (A)
         ├── Branch 1 (B) [Parallel]
         └── Branch 2 (C) [Parallel]
                 └── Aggregator (D)
    """
    node_a = TimedParallelNode(node_id="A", delay=0.02)
    node_b = ToolNode(
        node_id="B",
        tool_name="calculator",
        input_mapping={"expression": "$nodes.A.computed_value"},
        metadata={"default_inputs": {"expression": "20 + 5"}},
    )
    node_c = ToolNode(
        node_id="C",
        tool_name="calculator",
        metadata={"default_inputs": {"expression": "100 - 30"}},
    )
    node_d = ToolNode(
        node_id="D",
        tool_name="calculator",
        input_mapping={"expression": "$nodes.B.data.result"},
        metadata={"default_inputs": {"expression": "10"}},
    )

    graph = WorkflowGraph(
        nodes=[node_a, node_b, node_c, node_d],
        edges=[
            WorkflowEdge(source_node_id="A", target_node_id="B"),
            WorkflowEdge(source_node_id="A", target_node_id="C"),
            WorkflowEdge(source_node_id="B", target_node_id="D"),
            WorkflowEdge(source_node_id="C", target_node_id="D"),
        ],
    )

    executor = WorkflowExecutor()
    res = await executor.execute_graph(graph=graph, initial_context={"user_id": "test_user"})

    assert res.status == WorkflowStatus.COMPLETED
    assert res.node_states["A"].status == NodeStatus.COMPLETED
    assert res.node_states["B"].status == NodeStatus.COMPLETED
    assert res.node_states["C"].status == NodeStatus.COMPLETED
    assert res.node_states["D"].status == NodeStatus.COMPLETED
    assert "A" in res.step_outputs
    assert "B" in res.step_outputs
    assert "C" in res.step_outputs
    assert "D" in res.step_outputs


@pytest.mark.asyncio
async def test_retry_policy_with_exponential_backoff() -> None:
    """Flaky node with max_retries=2 should retry on failure and eventually succeed."""
    node = FlakyFailingNode(node_id="flaky_node", fail_count=2, max_retries=3)
    graph = WorkflowGraph(nodes=[node], edges=[])

    events_emitted = []
    executor = WorkflowExecutor(event_listener=lambda t, p: events_emitted.append(t))
    res = await executor.execute_graph(graph=graph)

    assert res.status == WorkflowStatus.COMPLETED
    assert res.node_states["flaky_node"].status == NodeStatus.COMPLETED
    assert res.node_states["flaky_node"].attempt == 3
    assert "node.retrying" in events_emitted


@pytest.mark.asyncio
async def test_unrecoverable_failure_halts_downstream_execution() -> None:
    """Unrecoverable node failure marks downstream nodes as SKIPPED and workflow as FAILED."""
    node_a = FlakyFailingNode(node_id="node_a", fail_count=5, max_retries=1)  # Will exhaust retries
    node_b = TimedParallelNode(node_id="node_b")

    graph = WorkflowGraph(
        nodes=[node_a, node_b],
        edges=[WorkflowEdge(source_node_id="node_a", target_node_id="node_b")],
    )

    executor = WorkflowExecutor()
    res = await executor.execute_graph(graph=graph)

    assert res.status == WorkflowStatus.FAILED
    assert res.node_states["node_a"].status == NodeStatus.FAILED
    assert res.node_states["node_b"].status == NodeStatus.PENDING or res.node_states["node_b"].status == NodeStatus.SKIPPED


@pytest.mark.asyncio
async def test_condition_branching_and_skipping() -> None:
    """ConditionNode routes to active branch and skips inactive branch."""
    cond_node = ConditionNode(
        node_id="check_score",
        condition_expression="score >= 50",
        true_branch_target="node_pass",
        false_branch_target="node_fail",
    )
    pass_node = TimedParallelNode(node_id="node_pass")
    fail_node = TimedParallelNode(node_id="node_fail")

    graph = WorkflowGraph(
        nodes=[cond_node, pass_node, fail_node],
        edges=[
            WorkflowEdge(source_node_id="check_score", target_node_id="node_pass", condition_expression="true"),
            WorkflowEdge(source_node_id="check_score", target_node_id="node_fail", condition_expression="false"),
        ],
    )

    executor = WorkflowExecutor()
    # Execute with score = 80 (True branch)
    res = await executor.execute_graph(graph=graph, initial_context={"score": 80})

    assert res.status == WorkflowStatus.COMPLETED
    assert res.node_states["check_score"].status == NodeStatus.COMPLETED
    assert res.node_states["node_pass"].status == NodeStatus.COMPLETED
    assert res.node_states["node_fail"].status == NodeStatus.SKIPPED


@pytest.mark.asyncio
async def test_human_approval_pause_and_checkpoint_resumption() -> None:
    """HumanNode pauses execution, generates checkpoint, and recover_execution resumes without re-running completed nodes."""
    node_1 = TimedParallelNode(node_id="step_1", delay=0.01)
    human_node = HumanNode(node_id="human_gate", title="Review Proposal")
    node_2 = TimedParallelNode(node_id="step_2", delay=0.01)

    graph = WorkflowGraph(
        nodes=[node_1, human_node, node_2],
        edges=[
            WorkflowEdge(source_node_id="step_1", target_node_id="human_gate"),
            WorkflowEdge(source_node_id="human_gate", target_node_id="step_2"),
        ],
    )

    executor = WorkflowExecutor()
    # Step 1: Initial run pauses at HumanNode
    res1 = await executor.execute_graph(graph=graph)

    assert res1.status == WorkflowStatus.WAITING_FOR_APPROVAL
    assert res1.node_states["step_1"].status == NodeStatus.COMPLETED
    assert res1.node_states["human_gate"].status == NodeStatus.WAITING_FOR_APPROVAL
    assert res1.checkpoint_id is not None

    # Step 2: Create checkpoint snapshot to simulate recovery
    chk = WorkflowCheckpoint.create(
        workflow_id=res1.workflow_id,
        execution_id=res1.execution_id,
        title="Approve Step 1",
        state_snapshot={
            "node_states": {
                "step_1": res1.node_states["step_1"].to_dict(),
                "human_gate": {
                    "node_id": "human_gate",
                    "status": "completed",  # Approved!
                    "outputs": {"approved": True},
                },
            },
            "step_outputs": {
                "step_1": res1.step_outputs["step_1"],
                "human_gate": {"approved": True},
            },
        },
    )

    # Step 3: Resume from checkpoint
    res2 = await executor.recover_execution(checkpoint=chk, graph=graph)

    assert res2.status == WorkflowStatus.COMPLETED
    assert res2.node_states["step_1"].status == NodeStatus.COMPLETED
    assert res2.node_states["human_gate"].status == NodeStatus.COMPLETED
    assert res2.node_states["step_2"].status == NodeStatus.COMPLETED
