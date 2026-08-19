"""Unit tests for Research Conversations REST endpoints."""

from typing import Any

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.application import create_application
from app.dependencies import get_current_user_claims


@pytest.fixture
def mock_claims() -> dict[str, Any]:
    return {
        "sub": "11111111-1111-1111-1111-111111111111",
        "email": "testuser@twib.ai",
        "role": "admin",
    }


@pytest.fixture
def client(mock_claims: dict[str, Any]) -> TestClient:
    app = create_application()
    app.dependency_overrides[get_current_user_claims] = lambda: mock_claims
    return TestClient(app)


def test_list_conversations_empty(client: TestClient) -> None:
    response = client.get("/api/v1/agents/research/conversations")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)


def test_create_and_get_conversation(client: TestClient) -> None:
    # 1. Create conversation
    create_res = client.post(
        "/api/v1/agents/research/conversations",
        json={"title": "Operating Systems Research", "agent_type": "research"},
    )
    assert create_res.status_code == status.HTTP_201_CREATED
    conv_data = create_res.json()["data"]
    assert conv_data["title"] == "Operating Systems Research"
    conv_id = conv_data["id"]

    # 2. Get details
    get_res = client.get(f"/api/v1/agents/research/conversations/{conv_id}")
    assert get_res.status_code == status.HTTP_200_OK
    detail_data = get_res.json()["data"]
    assert detail_data["id"] == conv_id
    assert detail_data["messages"] == []

    # 3. Delete conversation
    del_res = client.delete(f"/api/v1/agents/research/conversations/{conv_id}")
    assert del_res.status_code == status.HTTP_200_OK
