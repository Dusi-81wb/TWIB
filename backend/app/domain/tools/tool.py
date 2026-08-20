"""Tool domain protocol and value models.

Defines the domain contract for executable tools in TWIB, including parameter schemas,
metadata, and execution results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol


@dataclass(frozen=True)
class ToolMetadata:
    """Immutable metadata describing a tool's identity and capabilities."""

    name: str
    description: str
    version: str = "1.0.0"
    category: str = "general"
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolResult:
    """Result of an executed tool."""

    tool_name: str
    success: bool
    data: Any = None
    error: str | None = None
    execution_time_seconds: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def ok(cls, tool_name: str, data: Any, duration: float = 0.0, **kwargs: Any) -> ToolResult:
        return cls(tool_name=tool_name, success=True, data=data, execution_time_seconds=duration, metadata=kwargs)

    @classmethod
    def fail(cls, tool_name: str, error: str, duration: float = 0.0, **kwargs: Any) -> ToolResult:
        return cls(tool_name=tool_name, success=False, error=error, execution_time_seconds=duration, metadata=kwargs)


class BaseTool(Protocol):
    """Domain protocol that all executable tools must implement."""

    @property
    def metadata(self) -> ToolMetadata:
        """Return tool metadata specification."""
        ...

    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the tool with given parameters asynchronously."""
        ...
