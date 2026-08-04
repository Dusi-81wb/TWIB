"""Tests for Workflow REST API endpoints."""

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


def test_workflow_api_flow(client: TestClient, auth_headers: dict[str, str]) -> None:
    # 1. List templates
    resp = client.get("/api/v1/workflows/templates", headers=auth_headers)
    assert resp.status_code == 200
    templates_data = resp.json()
    assert templates_data["total"] >= 8

    # 2. Create workflow
    create_payload = {
        "workflow_name": "API Workflow Test",
        "user_request": "Create automated tests",
    }
    resp = client.post("/api/v1/workflows", json=create_payload, headers=auth_headers)
    assert resp.status_code == 201
    wf_data = resp.json()
    wf_id = wf_data["workflow_id"]
    assert wf_data["workflow_name"] == "API Workflow Test"
    assert wf_data["workflow_status"] == "created"

    # 3. Get workflow details
    resp = client.get(f"/api/v1/workflows/{wf_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["workflow_id"] == wf_id

    # 4. Pause workflow
    resp = client.post(f"/api/v1/workflows/{wf_id}/pause", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["workflow_status"] == "paused"

    # 5. Cancel workflow
    resp = client.post(f"/api/v1/workflows/{wf_id}/cancel", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["workflow_status"] == "cancelled"

    # 6. Instantiate template
    instantiate_payload = {
        "user_request": "Build authentication microservice",
        "custom_name": "Instantiated Auth Service",
    }
    resp = client.post(
        "/api/v1/workflows/templates/tpl-software-dev/instantiate",
        json=instantiate_payload,
        headers=auth_headers,
    )
    assert resp.status_code == 201
    inst_data = resp.json()
    assert inst_data["workflow_name"] == "Instantiated Auth Service"
    assert len(inst_data["execution_steps"]) == 7
