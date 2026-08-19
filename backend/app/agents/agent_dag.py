"""Multi-Agent Dynamic DAG Models and Data Structures.

Defines schemas and validators for dynamic agent graphs, node dependencies,
topological validation, cycle detection, and execution trace reporting.
"""

from __future__ import annotations

from collections import defaultdict, deque
from enum import StrEnum
from typing import Any
import uuid

from pydantic import BaseModel, Field

from app.agents.exceptions import AgentValidationError


class NodeStatus(StrEnum):
    """Execution status of an individual agent node within a DAG."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class AgentNode(BaseModel):
    """Specification of an individual agent node in an execution DAG.

    Attributes:
        node_id: Unique identifier for this node within the DAG.
        agent_id: Identifier of the agent to execute (e.g., 'research', 'analyst').
        name: Human-friendly display name.
        description: Description of the node's specific purpose.
        dependencies: List of prerequisite node_ids that must complete before this node.
        input_prompt_override: Optional specialized prompt override for this step.
        optional: If True, failures in this node will not abort downstream execution.
        max_retries: Number of retry attempts on failure.
        retry_delay_seconds: Initial backoff delay between retries.
    """

    node_id: str = Field(..., description="Unique identifier for this node in the graph.")
    agent_id: str = Field(..., description="Target agent identifier.")
    name: str = Field(default="", description="Display name for the execution step.")
    description: str = Field(default="", description="Summary of step objective.")
    dependencies: list[str] = Field(
        default_factory=list,
        description="List of node_ids that must complete before this node can run.",
    )
    input_prompt_override: str | None = Field(
        default=None,
        description="Optional custom prompt instructions tailored for this node.",
    )
    optional: bool = Field(
        default=False,
        description="If True, downstream execution continues even if this node fails.",
    )
    max_retries: int = Field(
        default=1,
        ge=0,
        le=5,
        description="Maximum retry attempts on execution failure.",
    )
    retry_delay_seconds: float = Field(
        default=0.5,
        ge=0.0,
        le=10.0,
        description="Base retry backoff delay in seconds.",
    )


class AgentDAGPlan(BaseModel):
    """A planned Directed Acyclic Graph (DAG) for multi-agent execution."""

    plan_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique ID for this planned execution graph.",
    )
    goal: str = Field(..., description="Primary user goal or request to fulfill.")
    rationale: str = Field(
        default="",
        description="Explanation of why this DAG structure and agent allocation was chosen.",
    )
    nodes: list[AgentNode] = Field(
        default_factory=list,
        description="List of agent nodes comprising the DAG.",
    )
    execution_strategy: str = Field(
        default="parallel_topological",
        description="Strategy used for dispatching nodes.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary plan-level metadata.",
    )

    def validate_graph(self) -> list[list[str]]:
        """Validate DAG structure for unknown dependencies and cyclic loops.

        Uses Kahn's algorithm to verify acyclicity and returns the nodes
        grouped into parallel execution waves (layers).

        Returns:
            List of node_id lists representing topological execution stages/waves.

        Raises:
            AgentValidationError: If a node has missing dependencies or if a cycle exists.
        """
        if not self.nodes:
            raise AgentValidationError(
                "AgentDAGPlan must contain at least one node",
                agent_id="supervisor",
            )

        node_map: dict[str, AgentNode] = {}
        for node in self.nodes:
            if node.node_id in node_map:
                raise AgentValidationError(
                    f"Duplicate node_id '{node.node_id}' in DAG plan",
                    agent_id="supervisor",
                )
            node_map[node.node_id] = node

        # Verify all dependencies reference valid nodes and self-references don't exist
        for node in self.nodes:
            for dep in node.dependencies:
                if dep == node.node_id:
                    raise AgentValidationError(
                        f"Node '{node.node_id}' cannot depend on itself (self-cycle)",
                        agent_id="supervisor",
                    )
                if dep not in node_map:
                    raise AgentValidationError(
                        f"Node '{node.node_id}' depends on non-existent node '{dep}'",
                        agent_id="supervisor",
                    )

        # Kahn's algorithm: compute in-degrees and build dependency graph
        in_degree: dict[str, int] = {node_id: 0 for node_id in node_map}
        outgoing: dict[str, list[str]] = defaultdict(list)

        for node in self.nodes:
            in_degree[node.node_id] = len(node.dependencies)
            for dep in node.dependencies:
                outgoing[dep].append(node.node_id)

        waves: list[list[str]] = []
        queue = deque([node_id for node_id, deg in in_degree.items() if deg == 0])
        processed_count = 0

        while queue:
            current_wave_size = len(queue)
            current_wave: list[str] = []
            for _ in range(current_wave_size):
                curr = queue.popleft()
                current_wave.append(curr)
                processed_count += 1
                for neighbor in outgoing[curr]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
            waves.append(current_wave)

        if processed_count < len(self.nodes):
            unprocessed = [
                node_id for node_id, deg in in_degree.items() if deg > 0
            ]
            raise AgentValidationError(
                f"Cyclic dependency detected involving nodes: {unprocessed}",
                agent_id="supervisor",
            )

        return waves

    def get_node(self, node_id: str) -> AgentNode | None:
        """Lookup node by its ID."""
        for n in self.nodes:
            if n.node_id == node_id:
                return n
        return None


class NodeExecutionRecord(BaseModel):
    """Execution status and output result for an individual DAG node."""

    node_id: str = Field(..., description="Target node identifier.")
    agent_id: str = Field(..., description="Executed agent identifier.")
    status: NodeStatus = Field(default=NodeStatus.PENDING, description="Current node state.")
    duration_seconds: float = Field(default=0.0, description="Execution duration in seconds.")
    retry_attempts: int = Field(default=0, description="Number of retries attempted.")
    result: Any = Field(default=None, description="Output generated by the agent.")
    error: str | None = Field(default=None, description="Error message if execution failed.")
    started_at: str | None = Field(default=None, description="ISO timestamp of start.")
    completed_at: str | None = Field(default=None, description="ISO timestamp of completion.")


class DAGExecutionResult(BaseModel):
    """Complete aggregated execution report for a dynamic multi-agent DAG."""

    plan_id: str = Field(..., description="Identifier of the executed DAG plan.")
    goal: str = Field(..., description="Original goal or user prompt.")
    status: NodeStatus = Field(..., description="Overall DAG execution status.")
    node_results: dict[str, NodeExecutionRecord] = Field(
        default_factory=dict,
        description="Mapping of node_id to execution records.",
    )
    final_result: Any = Field(
        default=None,
        description="Merged final output or result of terminal node(s).",
    )
    summary: str = Field(
        default="",
        description="Executive summary of the DAG run.",
    )
    total_duration_seconds: float = Field(
        default=0.0,
        description="Total duration of DAG execution.",
    )
    execution_graph: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Adjacency list of the executed graph (node_id -> list of child node_ids).",
    )
