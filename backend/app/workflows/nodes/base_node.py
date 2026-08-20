"""Workflow Base Node abstraction.

Defines the abstract base class and contract for all executable node types in a Workflow DAG,
including input resolution, schema validation, retries, timeouts, and serialization.
"""

from __future__ import annotations

import abc
import re
from typing import Any


class BaseWorkflowNode(abc.ABC):
    """Abstract base class for all nodes in a TWIB Workflow DAG."""

    def __init__(
        self,
        node_id: str,
        name: str = "",
        description: str = "",
        input_schema: dict[str, Any] | None = None,
        output_schema: dict[str, Any] | None = None,
        input_mapping: dict[str, str] | None = None,
        optional: bool = False,
        max_retries: int = 0,
        retry_delay_seconds: float = 0.5,
        timeout_seconds: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.node_id = node_id.strip() if node_id else ""
        self.name = name or self.node_id
        self.description = description
        self.input_schema = input_schema or {}
        self.output_schema = output_schema or {}
        self.input_mapping = input_mapping or {}
        self.optional = optional
        self.max_retries = max(0, max_retries)
        self.retry_delay_seconds = max(0.0, retry_delay_seconds)
        self.timeout_seconds = timeout_seconds
        self.metadata = metadata or {}

    @property
    @abc.abstractmethod
    def node_type(self) -> str:
        """Return the unique string discriminator for this node type."""
        ...

    def resolve_inputs(self, context_data: dict[str, Any], node_outputs: dict[str, Any]) -> dict[str, Any]:
        """Resolve input parameters based on input_mapping and available context and upstream outputs.

        Syntax supported:
        - "$context.key" -> context_data["key"]
        - "$nodes.node_id.key" -> node_outputs["node_id"]["key"]
        - "$nodes.node_id" -> node_outputs["node_id"]
        - literal values
        """
        resolved: dict[str, Any] = {}

        # Default copy from node's own metadata/inputs if provided
        for k, v in self.metadata.get("default_inputs", {}).items():
            resolved[k] = v

        for param_name, binding in self.input_mapping.items():
            if isinstance(binding, str) and binding.startswith("$"):
                parts = [p.strip() for p in binding[1:].split(".") if p.strip()]
                scope = parts[0] if parts else ""
                if scope == "context":
                    key_path = parts[1:]
                    val = self._extract_path(context_data, key_path)
                    if val is not None:
                        resolved[param_name] = val
                    elif param_name not in resolved:
                        resolved[param_name] = binding
                elif scope == "nodes" and len(parts) >= 2:
                    target_node = parts[1]
                    key_path = parts[2:]
                    target_out = node_outputs.get(target_node, {})
                    if key_path:
                        val = self._extract_path(target_out, key_path)
                        if val is not None:
                            resolved[param_name] = val
                        elif param_name not in resolved:
                            resolved[param_name] = binding
                    else:
                        resolved[param_name] = target_out
                else:
                    if param_name not in resolved:
                        resolved[param_name] = binding
            else:
                resolved[param_name] = binding


        return resolved

    @staticmethod
    def _extract_path(source: Any, path_parts: list[str]) -> Any:
        """Helper to safely traverse nested dicts or objects."""
        cur = source
        for p in path_parts:
            if isinstance(cur, dict):
                cur = cur.get(p)
            elif hasattr(cur, p):
                cur = getattr(cur, p)
            else:
                return None
        return cur

    def validate_node(self) -> list[str]:
        """Validate node configuration and return list of validation error messages."""
        errors: list[str] = []
        if not self.node_id:
            errors.append("node_id cannot be empty")
        return errors

    @abc.abstractmethod
    async def execute(
        self,
        inputs: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute node business logic asynchronously.

        Args:
            inputs: Resolved input parameters for this node.
            context: Global execution context dictionary.

        Returns:
            Dictionary of output values produced by this node.
        """
        ...

    def to_dict(self) -> dict[str, Any]:
        """Serialize node definition to a JSON-compatible dictionary."""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "input_mapping": self.input_mapping,
            "optional": self.optional,
            "max_retries": self.max_retries,
            "retry_delay_seconds": self.retry_delay_seconds,
            "timeout_seconds": self.timeout_seconds,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaseWorkflowNode:
        """Deserialize node instance from dictionary."""
        return cls(
            node_id=data.get("node_id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            input_schema=data.get("input_schema"),
            output_schema=data.get("output_schema"),
            input_mapping=data.get("input_mapping"),
            optional=data.get("optional", False),
            max_retries=data.get("max_retries", 0),
            retry_delay_seconds=data.get("retry_delay_seconds", 0.5),
            timeout_seconds=data.get("timeout_seconds"),
            metadata=data.get("metadata"),
        )

