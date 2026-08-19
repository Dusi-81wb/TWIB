"""Unit and integration tests for GET /api/v1/system/health."""

from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.dependencies import get_llm_gateway
from app.infrastructure.llm.gateway import LLMGateway


def test_basic_health_check_unmodified(client: TestClient) -> None:
    """Test GET /api/v1/health returns unmodified basic health structure."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "TWIB"
    assert "version" in data


def test_system_health_omniroute_connected(client: TestClient) -> None:
    """Test GET /api/v1/system/health returning connected OmniRoute metrics."""
    mock_gw = AsyncMock(spec=LLMGateway)
    mock_gw.health.return_value = {
        "status": "healthy",
        "provider": "omniroute",
        "latency_ms": 14.8,
        "base_url": "http://localhost:8080/v1",
    }
    mock_gw.default_model = "gpt-4o"
    mock_gw.base_url = "http://localhost:8080/v1"

    app = client.app
    app.dependency_overrides[get_llm_gateway] = lambda: mock_gw

    try:
        response = client.get("/api/v1/system/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

        omniroute = data["services"]["omniroute"]
        assert omniroute["status"] == "Connected"
        assert omniroute["connected"] is True
        assert omniroute["latency_ms"] == 14.8
        assert omniroute["configured_model"] == "gpt-4o"
        assert omniroute["base_url"] == "http://localhost:8080/v1"
    finally:
        app.dependency_overrides.pop(get_llm_gateway, None)


def test_system_health_omniroute_disconnected(client: TestClient) -> None:
    """Test GET /api/v1/system/health returning disconnected status when down."""
    mock_gw = AsyncMock(spec=LLMGateway)
    mock_gw.health.return_value = {
        "status": "unhealthy",
        "provider": "omniroute",
        "latency_ms": 0.0,
        "error": "Connection refused",
    }
    mock_gw.default_model = "best-free"
    mock_gw.base_url = "http://localhost:8080/v1"

    app = client.app
    app.dependency_overrides[get_llm_gateway] = lambda: mock_gw

    try:
        response = client.get("/api/v1/system/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"

        omniroute = data["services"]["omniroute"]
        assert omniroute["status"] == "Disconnected"
        assert omniroute["connected"] is False
        assert omniroute["configured_model"] == "best-free"
    finally:
        app.dependency_overrides.pop(get_llm_gateway, None)
