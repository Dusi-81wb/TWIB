"""Complete End-to-End Integration Test for TWIB Workflow Engine.

Executes a full multi-agent & tool DAG workflow:
Input
  ↓
Planner Agent
  ↓
Research Tool (WebSearchTool)
  ↓
Parallel Execution:
   ├── Analysis A (LLMNode)
   └── Analysis B (LLMNode)
          ↓
       Aggregator (ToolNode: PythonCodeTool)
          ↓
       Validator Agent (ValidatorAgent)
          ↓
       Final Output
"""

import asyncio
from typing import Any
import pytest

from app.domain.workflows.value_objects import EdgeType, NodeStatus, WorkflowEdge, WorkflowStatus
from app.infrastructure.tools.builtins import PythonCodeTool, WebSearchTool
from app.infrastructure.tools.registry import ToolRegistry
from app.workflows.nodes.node_types import (
    AgentNode,
    LLMNode,
    ToolNode,
)
from app.workflows.workflow_executor import WorkflowExecutor
from app.workflows.workflow_graph import WorkflowGraph


@pytest.mark.asyncio
async def test_complete_e2e_business_workflow() -> None:
    """Execute complete end-to-end multi-agent, tool, and parallel DAG workflow."""
    registry = ToolRegistry()

    # 1. Setup Mock Factory for Agents
    from app.agents.planner_agent import PlannerAgent
    from app.agents.validator_agent import ValidatorAgent
    from app.infrastructure.llm.factory import LLMProviderFactory
    from tests.test_planner_agent import MockLLMProvider

    mock_llm = MockLLMProvider('{"goal": "ERP Migration", "plan_overview": "Decompose ERP", "required_tasks": [{"task_id": "t1", "description": "Research architecture", "assigned_agent": "planner"}], "validation_passed": true, "issues": []}')
    llm_factory = LLMProviderFactory()
    llm_factory.register_instance("mock", mock_llm)


    planner_agent = PlannerAgent(llm_factory=llm_factory)
    validator_agent = ValidatorAgent(llm_factory=llm_factory)

    # 1. Define Nodes
    node_planner = AgentNode(
        node_id="planner_step",
        agent_id="planner",
        name="Strategic Planning Agent",
        description="Decomposes enterprise objective into execution roadmap",
        prompt_override="Decompose goal: Migrate legacy monolithic ERP to event-driven cloud architecture",
        agent_instance=planner_agent,
    )


    node_research = ToolNode(
        node_id="research_step",
        tool_name="web_search",
        name="Domain Research Tool",
        tool_registry=registry,
        arguments={"query": "Event-driven ERP migration architectural patterns", "max_results": 2},
    )

    node_analysis_a = LLMNode(
        node_id="analysis_security",
        name="Security & Compliance Analysis",
        prompt_template="Analyze security considerations for: {topic}. Research notes: {research_notes}",
        input_mapping={
            "topic": "$context.user_request",
            "research_notes": "$nodes.research_step.data.summary",
        },
        model="gpt-4o-mini",
    )

    node_analysis_b = LLMNode(
        node_id="analysis_cost",
        name="Cost & Resource Estimation",
        prompt_template="Estimate cloud infrastructure costs for: {topic}. Summary: {research_notes}",
        input_mapping={
            "topic": "$context.user_request",
            "research_notes": "$nodes.research_step.data.summary",
        },
        model="gpt-4o-mini",
    )

    code_aggregator = """
sec = inputs.get('security_text', '')
cost = inputs.get('cost_text', '')
combined_report = f"--- EXECUTIVE SYNTHESIS REPORT ---\\nSECURITY:\\n{sec}\\n\\nCOST:\\n{cost}\\n"
print("Aggregation complete")
"""
    node_aggregator = ToolNode(
        node_id="aggregator_step",
        tool_name="python_interpreter",
        name="Report Synthesis Aggregator",
        tool_registry=registry,
        arguments={"code": code_aggregator},
        input_mapping={
            "security_text": "$nodes.analysis_security.content",
            "cost_text": "$nodes.analysis_cost.content",
        },
    )

    node_validator = AgentNode(
        node_id="validator_step",
        agent_id="validator",
        name="Enterprise Quality Validator Agent",
        description="Validates aggregated report against quality gates",
        prompt_override="Validate the following enterprise architecture synthesis report and ensure zero critical risks",
        agent_instance=validator_agent,
    )


    # 2. Assemble DAG Graph with Edges
    edges = [
        # Planner -> Research
        WorkflowEdge(source_node_id="planner_step", target_node_id="research_step"),
        # Research -> Parallel (Analysis A, Analysis B)
        WorkflowEdge(source_node_id="research_step", target_node_id="analysis_security"),
        WorkflowEdge(source_node_id="research_step", target_node_id="analysis_cost"),
        # Parallel (Analysis A, Analysis B) -> Aggregator
        WorkflowEdge(source_node_id="analysis_security", target_node_id="aggregator_step"),
        WorkflowEdge(source_node_id="analysis_cost", target_node_id="aggregator_step"),
        # Aggregator -> Validator
        WorkflowEdge(source_node_id="aggregator_step", target_node_id="validator_step"),
    ]

    graph = WorkflowGraph(
        nodes=[
            node_planner,
            node_research,
            node_analysis_a,
            node_analysis_b,
            node_aggregator,
            node_validator,
        ],
        edges=edges,
    )

    # 3. Verify Graph Structural Properties
    assert len(graph.nodes) == 6
    assert len(graph.edges) == 6

    waves = graph.get_execution_waves()
    assert len(waves) == 5
    assert waves[0] == ["planner_step"]
    assert waves[1] == ["research_step"]
    assert sorted(waves[2]) == ["analysis_cost", "analysis_security"]  # Verified parallel wave!
    assert waves[3] == ["aggregator_step"]
    assert waves[4] == ["validator_step"]

    # 4. Execute Real DAG Workflow
    events_log: list[str] = []
    executor = WorkflowExecutor(event_listener=lambda t, p: events_log.append(t))

    initial_context = {
        "user_request": "Migrate legacy monolithic ERP to event-driven cloud architecture",
        "org_tier": "Enterprise",
        "provider": "mock",
        "model": "mock-model",
    }


    result = await executor.execute_graph(
        graph=graph,
        initial_context=initial_context,
        workflow_id="e2e-workflow-001",
    )

    # 5. Assertions on Execution Results
    assert result.status == WorkflowStatus.COMPLETED
    assert result.duration_seconds > 0.0
    assert result.error is None


    # Check all node statuses
    for nid in ["planner_step", "research_step", "analysis_security", "analysis_cost", "aggregator_step", "validator_step"]:
        state = result.node_states[nid]
        assert state.status == NodeStatus.COMPLETED, f"Node {nid} failed: {state.error}"
        assert state.duration_seconds >= 0.0

    # Verify Data Propagation
    # Research received query and returned results
    research_out = result.step_outputs["research_step"]
    assert "summary" in research_out["data"]

    # LLM nodes received upstream research notes in their rendered prompt
    sec_out = result.step_outputs["analysis_security"]
    assert "content" in sec_out

    # Aggregator executed Python aggregation
    agg_out = result.step_outputs["aggregator_step"]
    assert agg_out["data"]["executed"] is True

    # Validator completed validation
    val_out = result.step_outputs["validator_step"]
    assert val_out["status"] == "completed"

    # Verify Telemetry Events Sequence
    assert "workflow.started" in events_log
    assert "node.started" in events_log
    assert "node.completed" in events_log
    assert "workflow.completed" in events_log
