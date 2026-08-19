"""Tests for the health check endpoint.

Only the HTTP infrastructure is covered here. Authentication, database,
repository, service, agent, LLM, and workflow-engine behavior is tested in
later phases once those subsystems exist.
"""

from fastapi.testclient import TestClient

from app.core.constants import SERVICE_NAME, VERSION
from app.schemas.response import HealthResponse


def test_health_returns_200(client: TestClient) -> None:
    """The health endpoint responds with HTTP 200."""
    response = client.get("/api/v1/health")

    assert response.status_code == 200


def test_health_matches_response_model(client: TestClient) -> None:
    """The body validates against the shared ``HealthResponse`` schema."""
    response = client.get("/api/v1/health")
    payload = HealthResponse.model_validate(response.json())

    assert payload.status == "healthy"
    assert payload.service == SERVICE_NAME
    assert payload.version == VERSION


def test_health_returns_json_content_type(client: TestClient) -> None:
    """The health endpoint responds with the JSON content type."""
    response = client.get("/api/v1/health")

    assert response.headers["content-type"] == "application/json"


def test_application_starts(client: TestClient) -> None:
    """The application factory produces a startable, fully wired app.

    The fixture enters the test client as a context manager, which runs the
    FastAPI lifespan handlers for startup and shutdown. This test also
    asserts the factory wired the settings and the container onto the
    application state.
    """
    assert client.app.state.settings is not None
    assert client.app.state.container is not None
    assert client.get("/api/v1/health").status_code == 200
