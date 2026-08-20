"""Tests for TWIB Tool Subsystem and Built-in Tools."""

import pytest

from app.infrastructure.tools.builtins import (
    CalculatorTool,
    HttpTool,
    JsonTransformTool,
    PythonCodeTool,
    WebSearchTool,
)
from app.infrastructure.tools.registry import ToolRegistry


@pytest.mark.asyncio
async def test_web_search_tool() -> None:
    """WebSearchTool should query and return structured search results and summary."""
    tool = WebSearchTool()
    res = await tool.execute(query="Distributed Saga Pattern", max_results=2)
    assert res.success is True
    assert res.tool_name == "web_search"
    assert "query" in res.data
    assert len(res.data["results"]) == 2
    assert "summary" in res.data


@pytest.mark.asyncio
async def test_calculator_tool() -> None:
    """CalculatorTool should safely evaluate mathematical expressions."""
    tool = CalculatorTool()
    res = await tool.execute(expression="(25 * 4) + 50 / 2 - 5")
    assert res.success is True
    assert res.data["result"] == 120.0

    # Power expression
    res2 = await tool.execute(expression="2 ** 8")
    assert res2.success is True
    assert res2.data["result"] == 256


@pytest.mark.asyncio
async def test_python_code_tool() -> None:
    """PythonCodeTool should execute sandboxed python statements."""
    tool = PythonCodeTool()
    code = """
nums = [1, 2, 3, 4, 5]
total = sum(nums)
squared = [x**2 for x in nums]
print(f"Total: {total}")
"""
    res = await tool.execute(code=code)
    assert res.success is True
    assert "Total: 15" in res.data["stdout"]
    assert res.data["locals"]["total"] == 15
    assert res.data["locals"]["squared"] == [1, 4, 9, 16, 25]


@pytest.mark.asyncio
async def test_python_code_tool_blocks_dangerous_calls() -> None:
    """PythonCodeTool must block dangerous system operations."""
    tool = PythonCodeTool()
    res = await tool.execute(code="import os; os.listdir('.')")
    assert res.success is False
    assert "forbidden" in res.error.lower()


@pytest.mark.asyncio
async def test_json_transform_tool() -> None:
    """JsonTransformTool filters and projects specified keys."""
    tool = JsonTransformTool()
    input_data = {"id": "item-1", "name": "TWIB", "secret": "xyz", "version": "2.0"}
    res = await tool.execute(data=input_data, keys=["name", "version"])
    assert res.success is True
    assert res.data["transformed"] == {"name": "TWIB", "version": "2.0"}


def test_tool_registry_management() -> None:
    """ToolRegistry registers defaults and allows lookups."""
    registry = ToolRegistry()
    assert registry.has_tool("web_search") is True
    assert registry.has_tool("calculator") is True
    assert registry.has_tool("python_interpreter") is True
    assert registry.has_tool("json_transform") is True

    tool = registry.get("calculator")
    assert tool is not None
    assert tool.name == "calculator"
