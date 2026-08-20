"""Tests for WorkflowGraph DAG Engine, Cycle Detection, Topological Waves, and Dynamic Mutation."""

import pytest

from app.domain.workflows.exceptions import (
    WorkflowCycleError,
    WorkflowNotFoundError,
    WorkflowValidationError,
)
from app.domain.workflows.value_objects import EdgeType, WorkflowEdge
from app.workflows.nodes.node_types import AgentNode, LLMNode, ToolNode
from app.workflows.workflow_graph import WorkflowGraph


def test_valid_sequential_dag() -> None:
    """Sequential DAG: A -> B -> C validates and computes correct waves."""
    nodes = [
        AgentNode(node_id="A", agent_id="planner"),
        AgentNode(node_id="B", agent_id="research"),
        AgentNode(node_id="C", agent_id="validator"),
    ]
    edges = [
        WorkflowEdge(source_node_id="A", target_node_id="B"),
        WorkflowEdge(source_node_id="B", target_node_id="C"),
    ]
    graph = WorkflowGraph(nodes=nodes, edges=edges)

    assert len(graph.nodes) == 3
    assert len(graph.edges) == 2

    waves = graph.get_execution_waves()
    assert waves == [["A"], ["B"], ["C"]]

    ordered = graph.get_topological_sort()
    assert ordered == ["A", "B", "C"]


def test_valid_diamond_parallel_dag() -> None:
    """Diamond DAG: A -> (B, C) -> D should produce 3 execution waves with B and C in parallel."""
    nodes = [
        AgentNode(node_id="A", agent_id="planner"),
        AgentNode(node_id="B", agent_id="research"),
        AgentNode(node_id="C", agent_id="analyst"),
        AgentNode(node_id="D", agent_id="architect"),
    ]
    edges = [
        WorkflowEdge(source_node_id="A", target_node_id="B"),
        WorkflowEdge(source_node_id="A", target_node_id="C"),
        WorkflowEdge(source_node_id="B", target_node_id="D"),
        WorkflowEdge(source_node_id="C", target_node_id="D"),
    ]
    graph = WorkflowGraph(nodes=nodes, edges=edges)

    waves = graph.get_execution_waves()
    assert len(waves) == 3
    assert waves[0] == ["A"]
    assert sorted(waves[1]) == ["B", "C"]
    assert waves[2] == ["D"]

    # Test independent ready nodes calculation
    ready_initial = graph.get_independent_ready_nodes(set())
    assert ready_initial == ["A"]

    ready_after_a = graph.get_independent_ready_nodes({"A"})
    assert ready_after_a == ["B", "C"]

    ready_after_b_only = graph.get_independent_ready_nodes({"A", "B"})
    assert ready_after_b_only == ["C"]

    ready_after_bc = graph.get_independent_ready_nodes({"A", "B", "C"})
    assert ready_after_bc == ["D"]


def test_cycle_detection_rejects_cyclic_loop() -> None:
    """Cyclic dependency A -> B -> C -> A must be detected and raise WorkflowCycleError."""
    nodes = [
        AgentNode(node_id="A", agent_id="planner"),
        AgentNode(node_id="B", agent_id="research"),
        AgentNode(node_id="C", agent_id="validator"),
    ]
    edges = [
        WorkflowEdge(source_node_id="A", target_node_id="B"),
        WorkflowEdge(source_node_id="B", target_node_id="C"),
        WorkflowEdge(source_node_id="C", target_node_id="A"),
    ]

    with pytest.raises(WorkflowCycleError) as exc_info:
        WorkflowGraph(nodes=nodes, edges=edges)

    err = exc_info.value
    assert "Cyclic dependency detected" in str(err)
    assert len(err.cycle_path) >= 2


def test_self_loop_detected() -> None:
    """Self-loop edge (A -> A) must raise WorkflowCycleError."""
    nodes = [AgentNode(node_id="A", agent_id="planner")]
    edges = [WorkflowEdge(source_node_id="A", target_node_id="A")]

    with pytest.raises(WorkflowCycleError):
        WorkflowGraph(nodes=nodes, edges=edges)


def test_missing_node_in_edge_raises_validation_error() -> None:
    """Edge referencing a non-existent node ID must raise WorkflowValidationError."""
    nodes = [AgentNode(node_id="A", agent_id="planner")]
    edges = [WorkflowEdge(source_node_id="A", target_node_id="MISSING")]

    with pytest.raises(WorkflowValidationError):
        WorkflowGraph(nodes=nodes, edges=edges)


def test_dynamic_graph_mutation_add_remove() -> None:
    """Dynamic graph mutation: add_node, add_edge, remove_node, remove_edge."""
    graph = WorkflowGraph()
    n1 = AgentNode(node_id="n1", agent_id="planner")
    n2 = ToolNode(node_id="n2", tool_name="web_search")
    n3 = AgentNode(node_id="n3", agent_id="validator")

    graph.add_node(n1)
    graph.add_node(n2)
    graph.add_node(n3)
    assert len(graph.nodes) == 3

    graph.add_edge("n1", "n2")
    graph.add_edge("n2", "n3")
    assert len(graph.edges) == 2
    assert graph.get_execution_waves() == [["n1"], ["n2"], ["n3"]]

    # Remove edge
    graph.remove_edge("n1", "n2")
    assert len(graph.edges) == 1

    # Remove node (also cleans up attached edges)
    graph.remove_node("n3")
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 0


def test_dynamic_mutation_cycle_rollback() -> None:
    """Adding an edge that would cause a cycle must fail and roll back cleanly."""
    graph = WorkflowGraph(
        nodes=[
            AgentNode(node_id="A", agent_id="planner"),
            AgentNode(node_id="B", agent_id="research"),
        ],
        edges=[
            WorkflowEdge(source_node_id="A", target_node_id="B"),
        ],
    )
    assert len(graph.edges) == 1

    # Attempt to add B -> A
    with pytest.raises(WorkflowCycleError):
        graph.add_edge("B", "A")

    # Graph remains valid and unchanged
    assert len(graph.edges) == 1
    assert graph.get_execution_waves() == [["A"], ["B"]]


def test_node_replacement() -> None:
    """Replacing a node preserves incident edge connectivity."""
    graph = WorkflowGraph(
        nodes=[
            AgentNode(node_id="A", agent_id="planner"),
            AgentNode(node_id="B", agent_id="research"),
            AgentNode(node_id="C", agent_id="validator"),
        ],
        edges=[
            WorkflowEdge(source_node_id="A", target_node_id="B"),
            WorkflowEdge(source_node_id="B", target_node_id="C"),
        ],
    )

    new_b = ToolNode(node_id="B", tool_name="web_search")
    graph.replace_node("B", new_b)

    assert graph.get_node("B").node_type == "tool"
    assert len(graph.edges) == 2
    assert graph.get_execution_waves() == [["A"], ["B"], ["C"]]


def test_serialization_and_deserialization() -> None:
    """Graph serialization to JSON and reconstruction from JSON."""
    graph = WorkflowGraph(
        nodes=[
            LLMNode(node_id="llm_step", prompt_template="Explain {topic}", model="gpt-4o"),
            ToolNode(node_id="tool_step", tool_name="calculator", arguments={"expression": "10+5"}),
        ],
        edges=[
            WorkflowEdge(source_node_id="llm_step", target_node_id="tool_step", edge_type=EdgeType.SEQUENCE),
        ],
    )

    json_str = graph.to_json()
    reconstructed = WorkflowGraph.from_json(json_str)

    assert len(reconstructed.nodes) == 2
    assert reconstructed.get_node("llm_step").node_type == "llm"
    assert reconstructed.get_node("tool_step").node_type == "tool"
    assert len(reconstructed.edges) == 1
    assert reconstructed.edges[0].source_node_id == "llm_step"
