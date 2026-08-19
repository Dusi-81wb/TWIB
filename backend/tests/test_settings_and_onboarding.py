"""Tests for Settings, Onboarding, and Real Dashboard API endpoints."""

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


def test_onboarding_status_endpoint(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.get("/api/v1/settings/onboarding/status", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "onboarding_completed" in data
    assert "workspace_configured" in data
    assert "omniroute_configured" in data
    assert "services_health" in data


def test_omniroute_config_get_and_update(client: TestClient, auth_headers: dict[str, str]) -> None:
    # 1. Get current config
    resp = client.get("/api/v1/settings/omniroute", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "base_url" in data
    assert "default_model" in data
    assert "is_configured" in data

    # 2. Update config
    update_resp = client.put(
        "/api/v1/settings/omniroute",
        json={
            "omniroute_api_key": "sk-test-omniroute-key-12345",
            "omniroute_base_url": "http://localhost:8080/v1",
            "default_model": "best-free",
        },
        headers=auth_headers,
    )
    assert update_resp.status_code == 200
    up_data = update_resp.json()["data"]
    assert up_data["is_configured"] is True
    assert up_data["default_model"] == "best-free"
    assert "sk-t...2345" in up_data["masked_api_key"]


def test_onboarding_complete_endpoint(client: TestClient, auth_headers: dict[str, str]) -> None:
    payload = {
        "workspace_name": "Test Engineering Workspace",
        "workspace_purpose": "AI Agent Orchestration",
        "workspace_description": "Production test workspace",
        "omniroute_api_key": "sk-omniroute-live-production-key",
        "omniroute_base_url": "http://localhost:8080/v1",
        "default_model": "best-free",
    }
    resp = client.post("/api/v1/settings/onboarding/complete", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["success"] is True
    assert data["default_model"] == "best-free"


def test_omniroute_models_endpoint(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.get("/api/v1/settings/omniroute/models", headers=auth_headers)
    assert resp.status_code == 200
    models = resp.json()["data"]
    assert isinstance(models, list)
    assert len(models) > 0
    assert "best-free" in models


def test_dashboard_metrics_endpoint(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.get("/api/v1/monitoring/dashboard", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_workflows" in data
    assert "active_workflows" in data
    assert "completed_workflows" in data
    assert "failed_workflows" in data
    assert "total_agents" in data
    assert data["total_agents"] == 8
    assert "recent_executions" in data
    assert "recent_workflows" in data
    assert "services_status" in data
    assert "postgres" in data["services_status"]
