"""Infrastructure Base Tool implementation.

Provides standard execution wrappers, parameter validation against schemas, and timing telemetry.
"""

from __future__ import annotations

import abc
import time
from typing import Any

from app.domain.tools.tool import BaseTool, ToolMetadata, ToolResult


class AbstractTool(BaseTool, abc.ABC):
    """Abstract base class for TWIB infrastructure tools with schema validation and error wrapping."""

    def __init__(
        self,
        name: str,
        description: str,
        version: str = "1.0.0",
        category: str = "general",
        input_schema: dict[str, Any] | None = None,
        output_schema: dict[str, Any] | None = None,
    ) -> None:
        self._metadata = ToolMetadata(
            name=name,
            description=description,
            version=version,
            category=category,
            input_schema=input_schema or {},
            output_schema=output_schema or {},
        )

    @property
    def metadata(self) -> ToolMetadata:
        return self._metadata

    @property
    def name(self) -> str:
        return self._metadata.name

    @property
    def description(self) -> str:
        return self._metadata.description

    async def execute(self, **kwargs: Any) -> ToolResult:
        """Standard execution wrapper with error catching and timing telemetry."""
        start_time = time.perf_counter()
        try:
            # Validate input parameters if required fields are specified
            required_fields = self.metadata.input_schema.get("required", [])
            for field in required_fields:
                if field not in kwargs:
                    return ToolResult.fail(
                        tool_name=self.name,
                        error=f"Missing required parameter '{field}'",
                        duration=time.perf_counter() - start_time,
                    )

            result_data = await self._run(**kwargs)
            duration = time.perf_counter() - start_time
            return ToolResult.ok(tool_name=self.name, data=result_data, duration=duration)
        except Exception as exc:
            duration = time.perf_counter() - start_time
            return ToolResult.fail(tool_name=self.name, error=str(exc), duration=duration)

    @abc.abstractmethod
    async def _run(self, **kwargs: Any) -> Any:
        """Core execution logic to be implemented by concrete tools."""
        ...
