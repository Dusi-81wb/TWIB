"""Workflow DAG Graph Data Structure and Validation Engine.

Provides the comprehensive WorkflowGraph implementation supporting:
- Node registration and validation
- Directed edge management with conditions and metadata
- Cycle detection with exact cycle path reporting
- Topological sorting and parallel wave computation
- Independent ready-node detection
- Safe dynamic graph mutation (add_node, remove_node, add_edge, remove_edge, replace_node) with rollback on invalid structures
- JSON serialization and deserialization
"""

from __future__ import annotations

from collections import defaultdict, deque
import copy
import json
from typing import Any

from app.domain.workflows.exceptions import (
    WorkflowCycleError,
    WorkflowNotFoundError,
    WorkflowValidationError,
)
from app.domain.workflows.value_objects import EdgeType, WorkflowEdge
from app.workflows.nodes.base_node import BaseWorkflowNode
from app.workflows.nodes.node_types import create_node_from_dict


class WorkflowGraph:
    """Directed Acyclic Graph (DAG) for business workflow definition, validation, and dynamic mutation."""

    def __init__(
        self,
        nodes: list[BaseWorkflowNode] | None = None,
        edges: list[WorkflowEdge] | None = None,
    ) -> None:
        self._nodes: dict[str, BaseWorkflowNode] = {}
        self._edges: list[WorkflowEdge] = []
        self._outgoing: dict[str, list[WorkflowEdge]] = defaultdict(list)
        self._incoming: dict[str, list[WorkflowEdge]] = defaultdict(list)

        if nodes:
            for node in nodes:
                self.add_node(node, auto_validate=False)

        if edges:
            for edge in edges:
                self.add_edge(
                    source_node_id=edge.source_node_id,
                    target_node_id=edge.target_node_id,
                    edge_type=edge.edge_type,
                    condition=edge.condition_expression,
                    metadata=edge.metadata,
                    auto_validate=False,
                )

        # Validate on initial construction
        self.validate()

    @property
    def nodes(self) -> dict[str, BaseWorkflowNode]:
        """Return shallow copy of registered nodes keyed by node_id."""
        return dict(self._nodes)

    @property
    def edges(self) -> list[WorkflowEdge]:
        """Return copy of edges in the graph."""
        return list(self._edges)

    def get_node(self, node_id: str) -> BaseWorkflowNode:
        """Retrieve node by ID or raise WorkflowNotFoundError."""
        if node_id not in self._nodes:
            raise WorkflowNotFoundError(f"Node '{node_id}' not found in workflow graph")
        return self._nodes[node_id]

    def has_node(self, node_id: str) -> bool:
        """Check if node exists in graph."""
        return node_id in self._nodes

    def get_outgoing_edges(self, node_id: str) -> list[WorkflowEdge]:
        """Get all outgoing directed edges starting from node_id."""
        return list(self._outgoing.get(node_id, []))

    def get_incoming_edges(self, node_id: str) -> list[WorkflowEdge]:
        """Get all incoming directed edges pointing to node_id."""
        return list(self._incoming.get(node_id, []))

    def get_dependencies(self, node_id: str) -> list[str]:
        """Get list of immediate prerequisite node IDs for a given node."""
        return [edge.source_node_id for edge in self.get_incoming_edges(node_id)]

    def get_dependents(self, node_id: str) -> list[str]:
        """Get list of immediate downstream node IDs dependent on a given node."""
        return [edge.target_node_id for edge in self.get_outgoing_edges(node_id)]

    # =========================================================================
    # Dynamic Safe Graph Mutation
    # =========================================================================

    def add_node(self, node: BaseWorkflowNode, auto_validate: bool = True) -> None:
        """Add a node to the graph and optionally revalidate.

        Raises:
            WorkflowValidationError: If node with identical ID already exists or node is invalid.
        """
        if not node.node_id:
            raise WorkflowValidationError("Cannot add node with empty node_id")
        if node.node_id in self._nodes:
            raise WorkflowValidationError(f"Node with id '{node.node_id}' already exists in graph")

        errors = node.validate_node()
        if errors:
            raise WorkflowValidationError(f"Invalid node configuration for '{node.node_id}': {', '.join(errors)}")

        snapshot_nodes = dict(self._nodes)
        snapshot_edges = list(self._edges)

        self._nodes[node.node_id] = node

        if auto_validate:
            try:
                self.validate()
            except Exception:
                self._restore_snapshot(snapshot_nodes, snapshot_edges)
                raise

    def remove_node(self, node_id: str, auto_validate: bool = True) -> None:
        """Remove a node and its attached edges from the graph.

        Raises:
            WorkflowNotFoundError: If node_id does not exist.
        """
        if node_id not in self._nodes:
            raise WorkflowNotFoundError(f"Cannot remove non-existent node '{node_id}'")

        snapshot_nodes = dict(self._nodes)
        snapshot_edges = list(self._edges)

        del self._nodes[node_id]
        # Remove all connected edges
        self._edges = [e for e in self._edges if e.source_node_id != node_id and e.target_node_id != node_id]
        self._rebuild_adjacency()

        if auto_validate:
            try:
                self.validate()
            except Exception:
                self._restore_snapshot(snapshot_nodes, snapshot_edges)
                raise

    def add_edge(
        self,
        source_node_id: str,
        target_node_id: str,
        edge_type: EdgeType = EdgeType.SEQUENCE,
        condition: str | None = None,
        metadata: dict[str, Any] | None = None,
        auto_validate: bool = True,
    ) -> WorkflowEdge:
        """Add a directed edge from source_node_id to target_node_id.

        Raises:
            WorkflowValidationError: If source or target node is missing, or self-loop.
            WorkflowCycleError: If adding the edge introduces a cycle.
        """
        if source_node_id == target_node_id:
            raise WorkflowCycleError([source_node_id, target_node_id])

        if source_node_id not in self._nodes:
            raise WorkflowValidationError(f"Source node '{source_node_id}' does not exist in graph")
        if target_node_id not in self._nodes:
            raise WorkflowValidationError(f"Target node '{target_node_id}' does not exist in graph")

        edge = WorkflowEdge(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            edge_type=edge_type,
            condition_expression=condition,
            metadata=metadata or {},
        )

        # Check for duplicate edge
        for existing in self._edges:
            if existing.source_node_id == source_node_id and existing.target_node_id == target_node_id:
                return existing

        snapshot_nodes = dict(self._nodes)
        snapshot_edges = list(self._edges)

        self._edges.append(edge)
        self._outgoing[source_node_id].append(edge)
        self._incoming[target_node_id].append(edge)

        if auto_validate:
            try:
                self.validate()
            except Exception:
                self._restore_snapshot(snapshot_nodes, snapshot_edges)
                raise

        return edge

    def remove_edge(self, source_node_id: str, target_node_id: str, auto_validate: bool = True) -> None:
        """Remove a directed edge between two nodes."""
        snapshot_nodes = dict(self._nodes)
        snapshot_edges = list(self._edges)

        initial_len = len(self._edges)
        self._edges = [
            e for e in self._edges
            if not (e.source_node_id == source_node_id and e.target_node_id == target_node_id)
        ]

        if len(self._edges) == initial_len:
            raise WorkflowValidationError(f"No edge found from '{source_node_id}' to '{target_node_id}'")

        self._rebuild_adjacency()

        if auto_validate:
            try:
                self.validate()
            except Exception:
                self._restore_snapshot(snapshot_nodes, snapshot_edges)
                raise

    def replace_node(self, node_id: str, new_node: BaseWorkflowNode, auto_validate: bool = True) -> None:
        """Replace an existing node preserving all incident edges."""
        if node_id not in self._nodes:
            raise WorkflowNotFoundError(f"Cannot replace non-existent node '{node_id}'")

        snapshot_nodes = dict(self._nodes)
        snapshot_edges = list(self._edges)

        # If new_node ID is different from old node_id, update edge endpoints
        if new_node.node_id != node_id:
            if new_node.node_id in self._nodes:
                raise WorkflowValidationError(f"Node id '{new_node.node_id}' already exists")
            del self._nodes[node_id]
            self._nodes[new_node.node_id] = new_node
            new_edges = []
            for e in self._edges:
                src = new_node.node_id if e.source_node_id == node_id else e.source_node_id
                dst = new_node.node_id if e.target_node_id == node_id else e.target_node_id
                new_edges.append(
                    WorkflowEdge(
                        source_node_id=src,
                        target_node_id=dst,
                        edge_type=e.edge_type,
                        condition_expression=e.condition_expression,
                        metadata=e.metadata,
                    )
                )
            self._edges = new_edges
            self._rebuild_adjacency()
        else:
            self._nodes[node_id] = new_node

        if auto_validate:
            try:
                self.validate()
            except Exception:
                self._restore_snapshot(snapshot_nodes, snapshot_edges)
                raise

    def _rebuild_adjacency(self) -> None:
        """Reconstruct internal lookup tables from the edges list."""
        self._outgoing = defaultdict(list)
        self._incoming = defaultdict(list)
        for edge in self._edges:
            self._outgoing[edge.source_node_id].append(edge)
            self._incoming[edge.target_node_id].append(edge)

    def _restore_snapshot(
        self,
        snapshot_nodes: dict[str, BaseWorkflowNode],
        snapshot_edges: list[WorkflowEdge],
    ) -> None:
        """Rollback state to snapshot on validation failure."""
        self._nodes = dict(snapshot_nodes)
        self._edges = list(snapshot_edges)
        self._rebuild_adjacency()

    # =========================================================================
    # DAG Validation, Cycle Detection & Topological Ordering
    # =========================================================================

    def validate(self) -> None:
        """Validate entire graph structure for dangling edges and cycles."""
        # 1. Validate all edge endpoints exist
        for edge in self._edges:
            if edge.source_node_id not in self._nodes:
                raise WorkflowValidationError(f"Edge references non-existent source node '{edge.source_node_id}'")
            if edge.target_node_id not in self._nodes:
                raise WorkflowValidationError(f"Edge references non-existent target node '{edge.target_node_id}'")

        # 2. Cycle detection using DFS with recursion stack tracking
        self._detect_cycle_dfs()

    def _detect_cycle_dfs(self) -> None:
        """Detect cycles using DFS and report the exact cycle path if found."""
        visited: dict[str, int] = {nid: 0 for nid in self._nodes}  # 0=unvisited, 1=visiting, 2=visited
        parent_map: dict[str, str] = {}

        for start_node in self._nodes:
            if visited[start_node] == 0:
                stack = [start_node]
                path = [start_node]

                while stack:
                    curr = stack[-1]
                    if visited[curr] == 0:
                        visited[curr] = 1

                    found_unvisited_neighbor = False
                    for edge in self.get_outgoing_edges(curr):
                        neighbor = edge.target_node_id
                        if visited[neighbor] == 1:
                            # Cycle detected! Reconstruct the cycle loop
                            cycle_path = []
                            try:
                                cycle_start_idx = path.index(neighbor)
                                cycle_path = path[cycle_start_idx:] + [neighbor]
                            except ValueError:
                                cycle_path = [curr, neighbor]
                            raise WorkflowCycleError(cycle_path)
                        elif visited[neighbor] == 0:
                            parent_map[neighbor] = curr
                            visited[neighbor] = 1
                            stack.append(neighbor)
                            path.append(neighbor)
                            found_unvisited_neighbor = True
                            break

                    if not found_unvisited_neighbor:
                        visited[curr] = 2
                        stack.pop()
                        if path and path[-1] == curr:
                            path.pop()

    def get_topological_sort(self) -> list[str]:
        """Compute flat topological ordering using Kahn's algorithm."""
        in_degree = {nid: len(self.get_incoming_edges(nid)) for nid in self._nodes}
        queue = deque([nid for nid, deg in in_degree.items() if deg == 0])
        ordered: list[str] = []

        while queue:
            node_id = queue.popleft()
            ordered.append(node_id)
            for edge in self.get_outgoing_edges(node_id):
                target = edge.target_node_id
                in_degree[target] -= 1
                if in_degree[target] == 0:
                    queue.append(target)

        if len(ordered) != len(self._nodes):
            # Fallback cycle detection
            self._detect_cycle_dfs()
            raise WorkflowValidationError("Graph contains a cycle or unresolved dependency")

        return ordered

    def get_execution_waves(self) -> list[list[str]]:
        """Compute parallel execution waves where independent nodes run in parallel within each wave."""
        if not self._nodes:
            return []

        in_degree = {nid: len(self.get_incoming_edges(nid)) for nid in self._nodes}
        current_wave = [nid for nid, deg in in_degree.items() if deg == 0]
        waves: list[list[str]] = []
        processed_count = 0

        while current_wave:
            waves.append(sorted(current_wave))
            processed_count += len(current_wave)
            next_wave: list[str] = []

            for node_id in current_wave:
                for edge in self.get_outgoing_edges(node_id):
                    target = edge.target_node_id
                    in_degree[target] -= 1
                    if in_degree[target] == 0:
                        next_wave.append(target)

            current_wave = next_wave

        if processed_count != len(self._nodes):
            self._detect_cycle_dfs()
            raise WorkflowValidationError("Failed to resolve execution waves: graph contains cycle")

        return waves

    def get_independent_ready_nodes(self, completed_node_ids: set[str]) -> list[str]:
        """Return all nodes whose prerequisite incoming dependencies are fully satisfied in completed_node_ids."""
        ready: list[str] = []
        for node_id in self._nodes:
            if node_id in completed_node_ids:
                continue
            deps = set(self.get_dependencies(node_id))
            if deps.issubset(completed_node_ids):
                ready.append(node_id)
        return sorted(ready)

    # =========================================================================
    # Serialization & Deserialization
    # =========================================================================

    def to_dict(self) -> dict[str, Any]:
        """Serialize complete WorkflowGraph to a JSON-compatible dictionary."""
        return {
            "nodes": [node.to_dict() for node in self._nodes.values()],
            "edges": [edge.to_dict() for edge in self._edges],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorkflowGraph:
        """Deserialize WorkflowGraph from a dictionary."""
        nodes_raw = data.get("nodes", [])
        edges_raw = data.get("edges", [])

        nodes: list[BaseWorkflowNode] = []
        for n_data in nodes_raw:
            nodes.append(create_node_from_dict(n_data))

        edges: list[WorkflowEdge] = []
        for e_data in edges_raw:
            edges.append(WorkflowEdge.from_dict(e_data))

        return cls(nodes=nodes, edges=edges)

    def to_json(self, indent: int = 2) -> str:
        """Serialize graph to formatted JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> WorkflowGraph:
        """Deserialize graph from JSON string."""
        return cls.from_dict(json.loads(json_str))
