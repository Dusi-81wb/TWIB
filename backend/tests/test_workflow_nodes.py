"""Tests for all 8 Workflow Node Types and Node Serialization."""

import pytest

from app.workflows.nodes.base_node import BaseWorkflowNode
from app.workflows.nodes.node_types import (
    AgentNode,
    ConditionNode,
    HumanNode,
    LLMNode,
    LoopNode,
    ParallelNode,
    SubworkflowNode,
    ToolNode,
    create_node_from_dict,
)


@pytest.mark.asyncio
async def test_llm_node_execution() -> None:
    """LLMNode renders prompt template with resolved inputs and executes."""
    node = LLMNode(
        node_id="llm_1",
        prompt_template="Analyze user goal: {goal} with budget {budget}",
        model="gpt-4o",
    )
    inputs = {"goal": "Launch microservices", "budget": "$50,000"}
    context = {"org_id": "org_1"}

    out = await node.execute(inputs=inputs, context=context)
    assert "content" in out
    assert "Launch microservices" in out["rendered_prompt"]
    assert out["model_used"] == "gpt-4o"

    # Test serialization
    data = node.to_dict()
    assert data["node_type"] == "llm"
    restored = create_node_from_dict(data)
    assert isinstance(restored, LLMNode)
    assert restored.prompt_template == node.prompt_template


@pytest.mark.asyncio
async def test_tool_node_execution() -> None:
    """ToolNode executes tool from ToolRegistry with mapped inputs."""
    node = ToolNode(
        node_id="tool_calc",
        tool_name="calculator",
        input_mapping={"expression": "$nodes.prev_step.expr"},
    )
    resolved_inputs = node.resolve_inputs(
        context_data={},
        node_outputs={"prev_step": {"expr": "100 * 5 + 20"}},
    )
    assert resolved_inputs["expression"] == "100 * 5 + 20"

    out = await node.execute(inputs=resolved_inputs, context={})
    assert out["data"]["result"] == 520.0


@pytest.mark.asyncio
async def test_condition_node_execution() -> None:
    """ConditionNode evaluates conditional expression and selects branch."""
    node = ConditionNode(
        node_id="cond_1",
        condition_expression="score >= 80",
        true_branch_target="deploy_prod",
        false_branch_target="send_alert",
    )

    # Pass condition
    out_true = await node.execute(inputs={"score": 95}, context={})
    assert out_true["decision"] is True
    assert out_true["branch"] == "true"
    assert out_true["target_node_id"] == "deploy_prod"

    # Fail condition
    out_false = await node.execute(inputs={"score": 60}, context={})
    assert out_false["decision"] is False
    assert out_false["branch"] == "false"
    assert out_false["target_node_id"] == "send_alert"


@pytest.mark.asyncio
async def test_loop_node_execution() -> None:
    """LoopNode iterates over items in collection and aggregates results."""
    node = LoopNode(
        node_id="loop_1",
        items_source="files",
        max_iterations=10,
    )
    inputs = {"files": ["doc1.pdf", "doc2.pdf", "doc3.pdf"]}
    out = await node.execute(inputs=inputs, context={})
    assert out["items_count"] == 3
    assert len(out["results"]) == 3
    assert out["results"][0]["item"] == "doc1.pdf"


@pytest.mark.asyncio
async def test_parallel_node_execution() -> None:
    """ParallelNode executes multiple branches concurrently."""
    node = ParallelNode(
        node_id="par_1",
        child_branches=[
            {"name": "Security Audit"},
            {"name": "Performance Benchmark"},
            {"name": "Compliance Scan"},
        ],
        max_concurrency=3,
    )
    out = await node.execute(inputs={}, context={})
    assert out["total_branches"] == 3
    assert len(out["branch_results"]) == 3
    assert out["branch_results"][0]["status"] == "completed"


@pytest.mark.asyncio
async def test_human_node_execution() -> None:
    """HumanNode pauses execution and creates approval review payload."""
    node = HumanNode(
        node_id="review_step",
        title="Approve Architecture Proposal",
        instructions="Ensure schema is compliant with GDPR",
        assigned_role="architect_lead",
    )
    out = await node.execute(inputs={"architecture_summary": "Clean Architecture DAG"}, context={})
    assert out["checkpoint_required"] is True
    assert out["status"] == "awaiting_approval"
    assert out["assigned_role"] == "architect_lead"
    assert out["review_data"]["architecture_summary"] == "Clean Architecture DAG"


@pytest.mark.asyncio
async def test_agent_node_execution() -> None:
    """AgentNode dispatches execution to a specialized TWIB agent."""
    from app.agents.planner_agent import PlannerAgent
    from tests.test_planner_agent import MockLLMProvider
    from app.infrastructure.llm.factory import LLMProviderFactory

    factory = LLMProviderFactory()
    factory.register_instance("mock", MockLLMProvider('{"goal": "Plan architecture", "plan_overview": "Overview", "required_tasks": [{"task_id": "t1", "description": "Step 1", "assigned_agent": "planner"}]}'))
    planner = PlannerAgent(llm_factory=factory)


    node = AgentNode(
        node_id="agent_planner",
        agent_id="planner",
        agent_instance=planner,
    )
    out = await node.execute(
        inputs={"prompt": "Plan microservices architecture for TWIB", "provider": "mock", "model": "mock-model"},
        context={"user_request": "Plan architecture"},
    )
    assert out["agent_id"] == "planner"
    assert out["status"] == "completed"
    assert "result" in out



@pytest.mark.asyncio
async def test_subworkflow_node_execution() -> None:
    """SubworkflowNode executes a child DAG workflow."""
    sub_graph_def = {
        "nodes": [
            {"node_id": "sub_n1", "node_type": "tool", "tool_name": "calculator", "arguments": {"expression": "50 * 2"}},
        ],
        "edges": [],
    }
    node = SubworkflowNode(
        node_id="sub_wf_step",
        subworkflow_graph=sub_graph_def,
    )
    out = await node.execute(inputs={}, context={})
    assert out["status"] == "completed"
    assert "sub_n1" in out["outputs"]
    assert out["outputs"]["sub_n1"]["data"]["result"] == 100.0


def test_node_factory_roundtrip() -> None:
    """Node factory reconstructs all 8 concrete node types from dictionaries."""
    node_types = ["llm", "tool", "condition", "loop", "parallel", "human", "agent", "subworkflow"]
    for ntype in node_types:
        node_dict = {"node_id": f"test_{ntype}", "node_type": ntype}
        if ntype == "llm":
            node_dict["prompt_template"] = "test prompt"
        elif ntype == "tool":
            node_dict["tool_name"] = "calculator"
        elif ntype == "condition":
            node_dict["condition_expression"] = "True"
        elif ntype == "loop":
            node_dict["items_source"] = "items"
        elif ntype == "agent":
            node_dict["agent_id"] = "planner"

        inst = create_node_from_dict(node_dict)
        assert isinstance(inst, BaseWorkflowNode)
        assert inst.node_type == ntype
