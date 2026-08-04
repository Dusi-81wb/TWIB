"""Tests for Monitoring REST API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.core.settings import ApplicationSettings
from app.security import JWTHelper


@pytest.fixture
def auth_headers() -> dict[str, str]:
    jwt_helper = JWTHelper(ApplicationSettings())
    token = jwt_helper.create_access_token(
        {"sub": "00000000-0000-0000-0000-000000000001", "email": "test@example.com"}
    )
    return {"Authorization": f"Bearer {token}"}


def test_monitoring_api_unauthenticated(client: TestClient) -> None:
    resp = client.get("/api/v1/monitoring/health")
    assert resp.status_code == 401


def test_monitoring_api_flow(client: TestClient, auth_headers: dict[str, str]) -> None:
    # 1. System Health
    resp = client.get("/api/v1/monitoring/health", headers=auth_headers)
    assert resp.status_code == 200
    health_data = resp.json()
    assert health_data["status"] == "healthy"
    assert health_data["postgres"]["status"] == "healthy"
    assert health_data["redis"]["status"] == "healthy"

    # 2. Create a workflow first
    create_resp = client.post(
        "/api/v1/workflows",
        json={"workflow_name": "Monitoring Test WF", "user_request": "Test request"},
        headers=auth_headers,
    )
    assert create_resp.status_code == 201
    wf_id = create_resp.json()["workflow_id"]

    # 3. Workflow metrics
    resp = client.get("/api/v1/monitoring/workflows", headers=auth_headers)
    assert resp.status_code == 200
    wf_metrics = resp.json()
    assert wf_metrics["total_workflows"] >= 1

    # 4. Workflow diagnostic details
    resp = client.get(f"/api/v1/monitoring/workflows/{wf_id}", headers=auth_headers)
    assert resp.status_code == 200
    wf_details = resp.json()
    assert wf_details["workflow_id"] == wf_id
    assert wf_details["current_state"] == "created"

    # 5. Agent metrics
    resp = client.get("/api/v1/monitoring/agents", headers=auth_headers)
    assert resp.status_code == 200

    # 6. Detailed system status
    resp = client.get("/api/v1/monitoring/system", headers=auth_headers)
    assert resp.status_code == 200

    # 7. Unified metrics
    resp = client.get("/api/v1/monitoring/metrics", headers=auth_headers)
    assert resp.status_code == 200
    unified = resp.json()
    assert "system_health" in unified
    assert "workflow_metrics" in unified
    assert "agent_metrics" in unified


def test_monitoring_workflow_not_found(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    resp = client.get(
        "/api/v1/monitoring/workflows/non-existent-wf", headers=auth_headers
    )
    assert resp.status_code == 404
