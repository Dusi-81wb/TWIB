"""Tests for Agent REST API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.agents import AgentRequest, AgentResponse, AgentStatus
from app.core.settings import ApplicationSettings
from app.dependencies import get_planner_agent, get_supervisor_agent
from app.security import JWTHelper


@pytest.fixture
def auth_headers() -> dict[str, str]:
    jwt_helper = JWTHelper(ApplicationSettings())
    token = jwt_helper.create_access_token(
        {"sub": "00000000-0000-0000-0000-000000000001", "email": "test@example.com"}
    )
    return {"Authorization": f"Bearer {token}"}


class MockAgent:
    """Mock agent for testing REST endpoint delegation."""

    def __init__(self, agent_id: str) -> None:
        self.agent_id = agent_id

    async def execute(self, request: AgentRequest) -> AgentResponse:
        return AgentResponse(
            agent_id=self.agent_id,
            status=AgentStatus.COMPLETED,
            result={
                "status": "success",
                "agent": self.agent_id,
                "prompt": request.user_prompt,
            },
        )


def test_agent_api_auth_enforced(client: TestClient) -> None:
    # Requests without auth headers should fail with 401
    resp = client.post("/api/v1/agents/planner/execute", json={"user_prompt": "Test"})
    assert resp.status_code == 401


def test_planner_agent_endpoint(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    app = client.app
    app.dependency_overrides[get_planner_agent] = lambda: MockAgent("planner")
    try:
        resp = client.post(
            "/api/v1/agents/planner/execute",
            json={"user_prompt": "Plan system redesign"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["agent_id"] == "planner"
        assert data["status"] == "completed"
        assert data["result"]["agent"] == "planner"
    finally:
        app.dependency_overrides.clear()


def test_supervisor_agent_endpoint(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    app = client.app
    app.dependency_overrides[get_supervisor_agent] = lambda: MockAgent("supervisor")
    try:
        resp = client.post(
            "/api/v1/agents/supervisor/execute",
            json={"user_prompt": "Orchestrate full workflow"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["agent_id"] == "supervisor"
        assert data["status"] == "completed"
    finally:
        app.dependency_overrides.clear()


def test_agent_endpoints_validation_error(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    # Empty payload missing user_prompt
    resp = client.post(
        "/api/v1/agents/planner/execute",
        json={},
        headers=auth_headers,
    )
    assert resp.status_code == 422
