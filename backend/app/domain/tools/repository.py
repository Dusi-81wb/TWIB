"""Tool registry domain repository interface."""

from __future__ import annotations

from typing import Protocol

from app.domain.tools.tool import BaseTool


class IToolRegistry(Protocol):
    """Domain interface for tool discovery and registration."""

    def register(self, tool: BaseTool) -> None:
        """Register a tool instance."""
        ...

    def get(self, name: str) -> BaseTool | None:
        """Get a tool by its unique name."""
        ...

    def list_tools(self) -> list[BaseTool]:
        """Return all registered tools."""
        ...

    def has_tool(self, name: str) -> bool:
        """Check if a tool exists."""
        ...
