"""Tests for extended DAG and Checkpoint REST API Endpoints."""

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


def test_validate_graph_endpoint_valid_dag(client: TestClient, auth_headers: dict[str, str]) -> None:
    """POST /api/v1/workflows/validate-graph returns is_valid=True with computed topological waves."""
    payload = {
        "graph": {
            "nodes": [
                {"node_id": "step_a", "node_type": "agent", "name": "Planner"},
                {"node_id": "step_b", "node_type": "tool", "name": "Researcher"},
                {"node_id": "step_c", "node_type": "agent", "name": "Validator"},
            ],
            "edges": [
                {"source_node_id": "step_a", "target_node_id": "step_b", "edge_type": "sequence"},
                {"source_node_id": "step_b", "target_node_id": "step_c", "edge_type": "sequence"},
            ],
        }
    }
    resp = client.post("/api/v1/workflows/validate-graph", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_valid"] is True
    assert data["execution_waves"] == [["step_a"], ["step_b"], ["step_c"]]
    assert data["topological_order"] == ["step_a", "step_b", "step_c"]


def test_validate_graph_endpoint_detects_cycle(client: TestClient, auth_headers: dict[str, str]) -> None:
    """POST /api/v1/workflows/validate-graph detects cycles and returns is_valid=False with cycle path."""
    payload = {
        "graph": {
            "nodes": [
                {"node_id": "node_1", "node_type": "agent"},
                {"node_id": "node_2", "node_type": "tool"},
            ],
            "edges": [
                {"source_node_id": "node_1", "target_node_id": "node_2"},
                {"source_node_id": "node_2", "target_node_id": "node_1"},
            ],
        }
    }
    resp = client.post("/api/v1/workflows/validate-graph", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_valid"] is False
    assert len(data["cycles_detected"]) >= 1


def test_create_and_execute_dag_workflow_via_api(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Full API workflow lifecycle: create with DAG definition -> execute -> get status."""
    create_payload = {
        "workflow_name": "Automated Research Pipeline",
        "user_request": "Research vector database optimizations",
        "graph_definition": {
            "nodes": [
                {"node_id": "search", "node_type": "tool", "tool_name": "web_search", "arguments": {"query": "vector indexing"}},
                {"node_id": "summary", "node_type": "llm", "input_mapping": {"topic": "$nodes.search.data.query"}, "metadata": {"prompt_template": "Summarize {topic}"}},
            ],
            "edges": [
                {"source_node_id": "search", "target_node_id": "summary"},
            ],
        },

    }
    resp = client.post("/api/v1/workflows", json=create_payload, headers=auth_headers)
    assert resp.status_code == 201
    wf_data = resp.json()
    wf_id = wf_data["workflow_id"]
    assert wf_data["workflow_name"] == "Automated Research Pipeline"

    # Execute workflow
    exec_resp = client.post(f"/api/v1/workflows/{wf_id}/execute", json={"context": {"user": "tester"}}, headers=auth_headers)
    assert exec_resp.status_code == 200
    exec_data = exec_resp.json()
    assert exec_data["workflow_status"] in ("completed", "running")
