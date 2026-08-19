"""Unit and integration tests for ResearchExecution persistence and history API."""

import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.agents.research_agent import ResearchAgent
from app.core.settings import ApplicationSettings
from app.dependencies import get_research_agent
from app.infrastructure.database.models.research_execution_model import (
    ResearchExecutionModel,
)
from app.infrastructure.database.session import session_scope
from app.infrastructure.llm.gateway import LLMGateway
from app.infrastructure.llm.models import GatewayResponse, GatewayUsage
from app.infrastructure.repositories.research_execution_repository import (
    SQLAlchemyResearchExecutionRepository,
)
from app.security import JWTHelper


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Fixture providing valid Authorization JWT headers."""
    jwt_helper = JWTHelper(ApplicationSettings())
    token = jwt_helper.create_access_token(
        {"sub": "00000000-0000-0000-0000-000000000001", "email": "test@example.com"}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_research_execution_repository() -> None:
    """Test repository create and list_by_user methods."""
    async with session_scope() as db_session:
        repo = SQLAlchemyResearchExecutionRepository(db_session)
        user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

        created = await repo.create(
            user_id=user_id,
            prompt="Explain vector search indexing",
            response="Vector search uses HNSW indexes.",
            provider="omniroute",
            model="best-free",
            latency_ms=25.4,
            usage={"prompt_tokens": 12, "completion_tokens": 16, "total_tokens": 28},
        )

        assert isinstance(created, ResearchExecutionModel)
        assert created.id is not None
        assert created.user_id == user_id
        assert created.prompt == "Explain vector search indexing"
        assert created.latency_ms == 25.4

        history = await repo.list_by_user(user_id)
        assert len(history) >= 1
        assert history[0].prompt == "Explain vector search indexing"


def test_get_research_history_unauthorized(client: TestClient) -> None:
    """Test GET /api/v1/agents/research/history without auth returns 401."""
    response = client.get("/api/v1/agents/research/history")
    assert response.status_code == 401


def test_get_research_history_success(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """Test GET /api/v1/agents/research/history returns user execution list."""
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
        # First execute a run to persist an execution entity
        run_res = client.post(
            "/api/v1/agents/research/run",
            headers=auth_headers,
            json={
                "prompt": "Explain Raft leader election",
                "temperature": 0.3,
                "model": "best-free",
            },
        )
        assert run_res.status_code == 200

        # Then fetch history
        history_res = client.get(
            "/api/v1/agents/research/history",
            headers=auth_headers,
        )
        assert history_res.status_code == 200
        data = history_res.json()
        assert data["success"] is True
        items = data["data"]
        assert isinstance(items, list)
        assert len(items) >= 1
        record = items[0]
        assert record["prompt"] == "Explain Raft leader election"
        assert record["provider"] == "omniroute"
        assert record["model"] == "best-free"
        assert record["latency_ms"] == 12.5
        assert "user_id" in record
        assert "created_at" in record
    finally:
        app.dependency_overrides.pop(get_research_agent, None)
