"""Unit and integration tests for ResearchAgent run method and POST endpoint."""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.agents.exceptions import AgentValidationError
from app.agents.research_agent import ResearchAgent
from app.core.settings import ApplicationSettings
from app.dependencies import get_research_agent
from app.infrastructure.llm.gateway import LLMGateway
from app.infrastructure.llm.models import GatewayResponse, GatewayUsage
from app.security import JWTHelper


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Fixture providing valid Authorization JWT headers."""
    jwt_helper = JWTHelper(ApplicationSettings())
    token = jwt_helper.create_access_token(
        {"sub": "00000000-0000-0000-0000-000000000001", "email": "test@example.com"}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_gateway() -> AsyncMock:
    """Fixture providing a mock LLMGateway."""
    gateway = AsyncMock(spec=LLMGateway)
    gateway.chat.return_value = GatewayResponse(
        answer="Distributed systems require consensus algorithms.",
        provider="omniroute",
        model="best-free",
        latency_ms=45.2,
        usage=GatewayUsage(prompt_tokens=15, completion_tokens=12, total_tokens=27),
    )
    return gateway


@pytest.mark.asyncio
async def test_research_agent_run_success(mock_gateway: AsyncMock) -> None:
    """Test ResearchAgent.run() calling LLMGateway.chat()."""
    agent = ResearchAgent(llm_gateway=mock_gateway)
    res = await agent.run(
        prompt="Explain consensus algorithms",
        temperature=0.3,
        model="best-free",
    )

    assert isinstance(res, GatewayResponse)
    assert res.answer == "Distributed systems require consensus algorithms."
    assert res.provider == "omniroute"
    assert res.model == "best-free"
    assert res.latency_ms == 45.2
    assert res.usage.total_tokens == 27

    mock_gateway.chat.assert_called_once()
    call_kwargs = mock_gateway.chat.call_args.kwargs
    assert call_kwargs["model"] == "best-free"
    assert call_kwargs["temperature"] == 0.3


@pytest.mark.asyncio
async def test_research_agent_run_validation_error(mock_gateway: AsyncMock) -> None:
    """Test ResearchAgent.run() raising AgentValidationError for empty prompt."""
    agent = ResearchAgent(llm_gateway=mock_gateway)
    with pytest.raises(AgentValidationError):
        await agent.run("   ")


def test_post_research_run_endpoint_unauthorized(client: TestClient) -> None:
    """Test POST /api/v1/agents/research/run without auth returns 401."""
    response = client.post(
        "/api/v1/agents/research/run",
        json={
            "prompt": "Explain raft consensus",
            "temperature": 0.3,
            "model": "best-free",
        },
    )
    assert response.status_code == 401


def test_post_research_run_endpoint_success(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """Test POST /api/v1/agents/research/run with auth returning success envelope."""
    mock_gw = AsyncMock(spec=LLMGateway)
    mock_gw.chat.return_value = GatewayResponse(
        answer="Raft operates by electing a leader.",
        provider="omniroute",
        model="best-free",
        latency_ms=12.5,
        usage=GatewayUsage(prompt_tokens=8, completion_tokens=6, total_tokens=14),
    )
    test_agent = ResearchAgent(llm_gateway=mock_gw)

    app = client.app
    app.dependency_overrides[get_research_agent] = lambda: test_agent

    try:
        response = client.post(
            "/api/v1/agents/research/run",
            headers=auth_headers,
            json={
                "prompt": "Explain Raft leader election",
                "temperature": 0.3,
                "model": "best-free",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        payload = data["data"]
        assert payload["answer"] == "Raft operates by electing a leader."
        assert payload["provider"] == "omniroute"
        assert payload["model"] == "best-free"
        assert payload["latency_ms"] == 12.5
        assert payload["usage"]["total_tokens"] == 14
    finally:
        app.dependency_overrides.pop(get_research_agent, None)
