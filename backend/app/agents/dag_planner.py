"""Dynamic Multi-Agent DAG Planner.

Leverages LLM reasoning with deterministic heuristic fallback to plan
an adaptive Directed Acyclic Graph (DAG) for multi-agent workflows.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any
import uuid

from app.agents.agent_dag import AgentDAGPlan, AgentNode
from app.agents.exceptions import AgentValidationError
from app.infrastructure.llm.conversation import Conversation
from app.infrastructure.llm.factory import LLMProviderFactory
from app.infrastructure.llm.response import ChatRequest

logger = logging.getLogger(__name__)

DAG_PLANNER_SYSTEM_PROMPT = """You are the TWIB Dynamic Multi-Agent DAG Planner.
Your role is to analyze a user goal or workflow objective, choose the appropriate specialized agents,
and organize them into an optimal Directed Acyclic Graph (DAG) with parallel execution branches where possible.

Available Specialized Agents:
- planner: Goal decomposition, milestone planning, initial task scoping.
- research: Information retrieval, domain knowledge, best practices.
- analyst: Feasibility evaluation, metric definitions, risk assessment.
- architect: System architecture, schema design, structural specifications.
- validator: Quality verification, constraint checking, security audits.
- optimizer: Performance optimization, latency/cost reduction, caching.
- documentation: Executive summaries, architecture docs, implementation guides.

Rules:
1. Maximize concurrency: Run independent tasks in parallel by setting shared dependencies (e.g., 'research' and 'analyst' can both depend on 'planner' and run concurrently).
2. Choose only the agents necessary for the requested goal.
3. Every dependency must reference a valid node_id defined in the nodes list.
4. Output MUST be valid JSON strictly adhering to the schema below without markdown commentary.

Output JSON Schema:
{
  "goal": "Target objective",
  "rationale": "Why this execution graph and concurrency structure was selected",
  "nodes": [
    {
      "node_id": "node_1",
      "agent_id": "planner",
      "name": "Deconstruct Goal",
      "description": "Break down the objective into milestones",
      "dependencies": [],
      "optional": false,
      "max_retries": 1
    },
    {
      "node_id": "node_2",
      "agent_id": "research",
      "name": "Domain Research",
      "description": "Gather relevant facts and patterns",
      "dependencies": ["node_1"],
      "optional": true,
      "max_retries": 2
    },
    {
      "node_id": "node_3",
      "agent_id": "analyst",
      "name": "Risk & Feasibility Analysis",
      "description": "Analyze technical constraints and metrics",
      "dependencies": ["node_1"],
      "optional": false,
      "max_retries": 1
    },
    {
      "node_id": "node_4",
      "agent_id": "architect",
      "name": "Architecture Design",
      "description": "Synthesize research and analysis into system design",
      "dependencies": ["node_2", "node_3"],
      "optional": false,
      "max_retries": 1
    }
  ]
}
"""


class DynamicDAGPlanner:
    """Intelligent dynamic planner that builds agent execution DAGs."""

    def __init__(
        self,
        llm_factory: LLMProviderFactory | None = None,
        default_model: str = "gpt-4o",
        default_provider: str = "openai",
    ) -> None:
        """Initialize DynamicDAGPlanner.

        Args:
            llm_factory: Factory for resolving LLM providers.
            default_model: Default model identifier.
            default_provider: Default provider identifier ('openai' or 'ollama').
        """
        self._llm_factory = llm_factory or LLMProviderFactory()
        self._default_model = default_model
        self._default_provider = default_provider

    async def plan_dag(
        self,
        goal: str,
        context: dict[str, Any] | None = None,
        provider: str | None = None,
        model: str | None = None,
        temperature: float = 0.2,
    ) -> AgentDAGPlan:
        """Plan a dynamic multi-agent DAG for the given goal.

        Attempts LLM planning first. If LLM execution or JSON parsing fails,
        falls back gracefully to an adaptive heuristic DAG.

        Args:
            goal: User goal or prompt.
            context: Optional contextual parameters.
            provider: Optional LLM provider override.
            model: Optional model override.
            temperature: LLM temperature for planning.

        Returns:
            Validated AgentDAGPlan ready for execution.
        """
        if not goal or not goal.strip():
            raise AgentValidationError(
                "Goal prompt cannot be empty for DAG planning",
                agent_id="dag_planner",
            )

        provider_name = provider or self._default_provider
        model_name = model or self._default_model
        ctx = context or {}

        # 1. Attempt LLM-based DAG generation if not forced to heuristic
        if not ctx.get("force_heuristic"):
            try:
                llm_provider = self._llm_factory.get_provider(provider_name)
                conv = Conversation()
                conv.add_system_message(DAG_PLANNER_SYSTEM_PROMPT)

                user_msg = f"Goal: {goal.strip()}"
                if ctx:
                    user_msg += f"\nContext: {json.dumps(ctx, default=str)}"
                conv.add_user_message(user_msg)

                chat_req = ChatRequest(
                    model=model_name,
                    messages=conv.messages,
                    temperature=temperature,
                    max_tokens=2048,
                )

                chat_res = await asyncio.wait_for(
                    llm_provider.complete(chat_req),
                    timeout=ctx.get("llm_timeout", 3.0),
                )

                plan = self._parse_llm_dag_response(goal, chat_res.message.content)
                plan.validate_graph()
                return plan
            except Exception as exc:
                logger.warning(
                    "LLM dynamic DAG planning failed or unavailable (%s). Using heuristic DAG generator.",
                    exc,
                )

        # 2. Heuristic fallback
        plan = self.generate_heuristic_dag(goal, ctx)
        plan.validate_graph()
        return plan

    def _parse_llm_dag_response(self, goal: str, content: str) -> AgentDAGPlan:
        """Extract and parse JSON DAG plan from raw LLM output."""
        cleaned = content.strip()
        if "```" in cleaned:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
            if match:
                cleaned = match.group(1).strip()

        data = json.loads(cleaned)
        nodes_data = data.get("nodes", [])
        nodes: list[AgentNode] = []
        for n in nodes_data:
            nodes.append(
                AgentNode(
                    node_id=str(n["node_id"]),
                    agent_id=str(n["agent_id"]),
                    name=str(n.get("name") or n["node_id"]),
                    description=str(n.get("description", "")),
                    dependencies=[str(d) for d in n.get("dependencies", [])],
                    input_prompt_override=n.get("input_prompt_override"),
                    optional=bool(n.get("optional", False)),
                    max_retries=int(n.get("max_retries", 1)),
                )
            )

        return AgentDAGPlan(
            plan_id=str(uuid.uuid4()),
            goal=goal,
            rationale=str(data.get("rationale", "LLM-generated adaptive DAG")),
            nodes=nodes,
            execution_strategy=str(data.get("execution_strategy", "parallel_topological")),
            metadata={"source": "llm_planner"},
        )

    def generate_heuristic_dag(
        self,
        goal: str,
        context: dict[str, Any] | None = None,
    ) -> AgentDAGPlan:
        """Generate an optimal deterministic DAG based on goal classification.

        Builds multi-stage DAGs with concurrent branches for comprehensive
        or specialized workflows.
        """
        goal_lower = goal.lower()
        ctx = context or {}

        # Specialized lightweight subgraphs for targeted tasks
        if "quick research" in goal_lower or "lookup" in goal_lower or "search only" in goal_lower:
            nodes = [
                AgentNode(
                    node_id="research_1",
                    agent_id="research",
                    name="Targeted Research",
                    description="Perform domain and context research",
                    dependencies=[],
                ),
                AgentNode(
                    node_id="doc_1",
                    agent_id="documentation",
                    name="Synthesize Findings",
                    description="Compile findings into summary document",
                    dependencies=["research_1"],
                ),
            ]
            rationale = "Targeted research pipeline with direct documentation synthesis."
        elif "validate" in goal_lower and "architecture" not in goal_lower and "plan" not in goal_lower:
            nodes = [
                AgentNode(
                    node_id="validator_1",
                    agent_id="validator",
                    name="Constraint & Quality Validation",
                    description="Verify compliance and check constraints",
                    dependencies=[],
                ),
                AgentNode(
                    node_id="optimizer_1",
                    agent_id="optimizer",
                    name="Optimization Analysis",
                    description="Identify optimization recommendations",
                    dependencies=["validator_1"],
                    optional=True,
                ),
            ]
            rationale = "Focused validation and optimization assessment pipeline."
        else:
            # Full Enterprise Workflow with Parallel Diamond Branches
            # Stage 1: Planning
            # Stage 2: Research & Analysis (Parallel)
            # Stage 3: Architecture Design
            # Stage 4: Validation & Optimization (Parallel)
            # Stage 5: Documentation Synthesis
            nodes = [
                AgentNode(
                    node_id="step_planner",
                    agent_id="planner",
                    name="Decompose Workflow Goal",
                    description="Formulate structured execution plan and milestones",
                    dependencies=[],
                ),
                AgentNode(
                    node_id="step_research",
                    agent_id="research",
                    name="Domain & Integration Research",
                    description="Retrieve technical specifications and patterns",
                    dependencies=["step_planner"],
                    optional=True,
                ),
                AgentNode(
                    node_id="step_analyst",
                    agent_id="analyst",
                    name="Feasibility & Metric Analysis",
                    description="Analyze constraints, dependencies, and risks",
                    dependencies=["step_planner"],
                ),
                AgentNode(
                    node_id="step_architect",
                    agent_id="architect",
                    name="System Architecture Design",
                    description="Design component topology and workflow specifications",
                    dependencies=["step_research", "step_analyst"],
                ),
                AgentNode(
                    node_id="step_validator",
                    agent_id="validator",
                    name="Constraint & Integrity Validation",
                    description="Verify compliance against architectural standards",
                    dependencies=["step_architect"],
                ),
                AgentNode(
                    node_id="step_optimizer",
                    agent_id="optimizer",
                    name="Performance & Cost Optimization",
                    description="Tuning workflow latency, token budget, and efficiency",
                    dependencies=["step_architect"],
                    optional=True,
                ),
                AgentNode(
                    node_id="step_documentation",
                    agent_id="documentation",
                    name="Documentation & Summary Synthesis",
                    description="Compile comprehensive technical documentation",
                    dependencies=["step_validator", "step_optimizer"],
                ),
            ]
            rationale = (
                "Comprehensive adaptive DAG featuring concurrent research/analysis "
                "and concurrent validation/optimization stages."
            )

        return AgentDAGPlan(
            plan_id=str(uuid.uuid4()),
            goal=goal,
            rationale=rationale,
            nodes=nodes,
            execution_strategy="parallel_topological",
            metadata={"source": "heuristic_planner", "context": ctx},
        )
