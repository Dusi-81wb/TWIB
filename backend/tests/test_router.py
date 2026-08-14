"""Tests for the root API router."""

from fastapi.testclient import TestClient

from app.api.router import api_router
from app.core.constants import API_PREFIX

def test_api_router_configuration() -> None:
    """Verify that the root API router is correctly configured."""
    # Ensure the root router has the correct prefix
    assert api_router.prefix == API_PREFIX

    # Check that the router includes sub-routes (v1 router)
    # The routes attribute will be a list of APIRoute or _IncludedRouter objects
    assert len(api_router.routes) > 0, "api_router should have nested routes"

def test_health_endpoint(client: TestClient) -> None:
    """Verify that the health endpoint works under the correct prefix."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
