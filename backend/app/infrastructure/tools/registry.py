"""Tool Registry implementation."""

from __future__ import annotations

from typing import Any

from app.domain.tools.repository import IToolRegistry
from app.domain.tools.tool import BaseTool
from app.infrastructure.tools.builtins import (
    CalculatorTool,
    HttpTool,
    JsonTransformTool,
    PythonCodeTool,
    WebSearchTool,
)


class ToolRegistry(IToolRegistry):
    """Central registry and execution manager for tools in TWIB."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register the built-in system tools."""
        self.register(WebSearchTool())
        self.register(CalculatorTool())
        self.register(PythonCodeTool())
        self.register(HttpTool())
        self.register(JsonTransformTool())

    def register(self, tool: BaseTool) -> None:
        """Register a tool instance."""
        self._tools[tool.metadata.name] = tool

    def get(self, name: str) -> BaseTool | None:
        """Retrieve a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[BaseTool]:
        """List all registered tools."""
        return list(self._tools.values())

    def has_tool(self, name: str) -> bool:
        """Check whether a tool is registered."""
        return name in self._tools
