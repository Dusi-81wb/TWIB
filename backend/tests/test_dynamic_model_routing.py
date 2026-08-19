"""Tests for dynamic model discovery and safe routing across LLM providers and workflows."""

import pytest
import httpx
from unittest.mock import AsyncMock, patch

from app.core.settings import ApplicationSettings
from app.infrastructure.llm.omniroute_gateway import OmniRouteGateway
from app.infrastructure.llm.providers.openai_provider import OpenAIProvider
from app.infrastructure.llm.response import ChatRequest
from app.infrastructure.llm.message import ChatMessage, MessageRole
from app.agents.research_agent import ResearchAgent
from app.agents.supervisor_agent import SupervisorAgent
from app.workflows.workflow import Workflow
from app.workflows.workflow_executor import WorkflowExecutor
from app.container import ApplicationContainer


@pytest.mark.asyncio
async def test_omniroute_gateway_dynamic_model_discovery_local_llm() -> None:
    """Test that OmniRouteGateway discovers local model and prevents sending 'best-fast' to LM Studio."""
    mock_models_response = {
        "data": [
            {
                "id": "liquid/lfm2.5-1.2b@q8_0",
                "object": "model",
                "loaded": True,
            }
        ]
    }
    mock_chat_response = {
        "id": "chatcmpl-mock-123",
        "model": "liquid/lfm2.5-1.2b@q8_0",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "Local model output verified."},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25},
    }

    async def mock_handler(request: httpx.Request) -> httpx.Response:
        url_str = str(request.url)
        if url_str.endswith("/models"):
            return httpx.Response(200, json=mock_models_response)
        elif url_str.endswith("/chat/completions"):
            import json
            payload = json.loads(request.content.decode("utf-8"))
            # Ensure "best-fast" or "default" was NOT sent to the backend!
            assert payload["model"] == "liquid/lfm2.5-1.2b@q8_0"
            return httpx.Response(200, json=mock_chat_response)
        return httpx.Response(404)

    transport = httpx.MockTransport(mock_handler)
    mock_client = httpx.AsyncClient(transport=transport)

    settings = ApplicationSettings(
        omniroute_base_url="http://127.0.0.1:1234/v1",
        default_model="best-fast",  # Generic strategy that shouldn't be sent to LM Studio!
        omniroute_api_key="",
    )

    gateway = OmniRouteGateway(settings=settings, http_client=mock_client)

    # When requesting "best-fast" (or default), gateway must resolve to "liquid/lfm2.5-1.2b@q8_0"
    res = await gateway.chat(
        [ChatMessage(role=MessageRole.USER, content="Hello local model")],
        model="best-fast",
    )

    assert res.answer == "Local model output verified."
    assert res.model == "liquid/lfm2.5-1.2b@q8_0"


@pytest.mark.asyncio
async def test_openai_provider_dynamic_model_discovery_local_llm() -> None:
    """Test that OpenAIProvider discovers local model and prevents sending generic placeholders."""
    settings = ApplicationSettings(
        omniroute_base_url="http://127.0.0.1:1234/v1",
        default_model="best-free",
        omniroute_api_key="",
    )
    provider = OpenAIProvider(settings=settings)

    # Mock list_models returning loaded LM Studio model
    with patch.object(
        provider,
        "list_models",
        new_callable=AsyncMock,
    ) as mock_list:
        from app.infrastructure.llm.models import ModelInfo
        mock_list.return_value = [
            ModelInfo(
                id="liquid/lfm2.5-1.2b@q8_0",
                name="liquid/lfm2.5-1.2b@q8_0",
                provider="openai",
            )
        ]

        resolved = await provider._resolve_target_model("best-fast")
        assert resolved == "liquid/lfm2.5-1.2b@q8_0"

        resolved_gpt4 = await provider._resolve_target_model("gpt-4o")
        assert resolved_gpt4 == "liquid/lfm2.5-1.2b@q8_0"

        resolved_none = await provider._resolve_target_model(None)
        assert resolved_none == "liquid/lfm2.5-1.2b@q8_0"


@pytest.mark.asyncio
async def test_research_agent_safe_model_routing() -> None:
    """Test ResearchAgent runs without forcing best-fast."""
    mock_gateway = AsyncMock(spec=OmniRouteGateway)
    from app.infrastructure.llm.models import GatewayResponse, GatewayUsage
    mock_gateway.chat.return_value = GatewayResponse(
        answer='{"topic": "Quantum", "summary": "Quantum computing overview", "key_findings": ["Superposition"]}',
        model="liquid/lfm2.5-1.2b@q8_0",
        provider="omniroute",
        latency_ms=120.0,
        usage=GatewayUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
    )

    agent = ResearchAgent(llm_gateway=mock_gateway)
    res = await agent.run("Quantum computing")

    assert res.model == "liquid/lfm2.5-1.2b@q8_0"
    # Ensure call to gateway was made with model=None (or resolved) rather than hardcoded "best-fast"
    call_kwargs = mock_gateway.chat.call_args[1]
    assert call_kwargs["model"] is None
