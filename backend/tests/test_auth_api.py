"""Integration tests for the Authentication API endpoints."""

from __future__ import annotations

from typing import Any, cast

from fastapi.testclient import TestClient

from app.dependencies import get_authentication_service
from app.domain.users.exceptions import EmailAlreadyAssigned


class MockAuthenticationService:
    """Mock AuthenticationService for API integration testing."""

    def __init__(self) -> None:
        self.users: dict[str, dict[str, Any]] = {}

    async def register_user(
        self,
        email: str,
        password: str,
        display_name: str | None = None,
        user_agent: str = "",
        ip_address: str = "",
    ) -> dict[str, Any]:
        """Mock implementation of register_user."""
        if email in self.users:
            raise EmailAlreadyAssigned(f"Email '{email}' is already registered")

        user_info = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": email,
            "display_name": display_name or email.split("@")[0],
            "role": "member",
            "status": "active",
        }
        self.users[email] = user_info

        return {
            "access_token": "mock_access_token_jwt",
            "refresh_token": "mock_refresh_token_string",
            "token_type": "bearer",
            "expires_in": 1800,
            "user": user_info,
        }


def test_register_user_api_success(client: TestClient) -> None:
    """Test POST /api/v1/auth/register creates user and returns tokens."""
    mock_service = MockAuthenticationService()
    app = cast(Any, client.app)
    app.dependency_overrides[get_authentication_service] = lambda: mock_service

    try:
        payload = {
            "email": "testregister@example.com",
            "password": "SecretPassword123!",
            "name": "Test Register User",
        }
        response = client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["access_token"] == "mock_access_token_jwt"  # noqa: S105
        assert data["token_type"] == "bearer"  # noqa: S105
        assert data["user"]["email"] == "testregister@example.com"
        assert data["user"]["display_name"] == "Test Register User"
        assert data["user"]["role"] == "member"
        assert data["user"]["status"] == "active"
    finally:
        app.dependency_overrides.clear()


def test_register_user_api_duplicate_email(client: TestClient) -> None:
    """Test POST /api/v1/auth/register fails with 409 Conflict on duplicate email."""
    mock_service = MockAuthenticationService()
    app = cast(Any, client.app)
    app.dependency_overrides[get_authentication_service] = lambda: mock_service

    try:
        payload = {
            "email": "duplicatereg@example.com",
            "password": "SecretPassword123!",
            "display_name": "First Registration",
        }

        res1 = client.post("/api/v1/auth/register", json=payload)
        assert res1.status_code == 201

        res2 = client.post("/api/v1/auth/register", json=payload)
        assert res2.status_code == 409
        body = res2.json()
        msg = body.get("detail") or body.get("error", {}).get("message", "")
        assert "already registered" in msg
    finally:
        app.dependency_overrides.clear()


def test_register_user_api_invalid_payload(client: TestClient) -> None:
    """Test POST /api/v1/auth/register fails with 422 for bad schema."""
    mock_service = MockAuthenticationService()
    app = cast(Any, client.app)
    app.dependency_overrides[get_authentication_service] = lambda: mock_service

    try:
        payload = {
            "email": "not-an-email",
            "password": "short",
        }
        response = client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_login_user_api_invalid_payload(client: TestClient) -> None:
    """Test POST /api/v1/auth/login fails with 422 for bad schema."""
    mock_service = MockAuthenticationService()
    app = cast(Any, client.app)
    app.dependency_overrides[get_authentication_service] = lambda: mock_service

    try:
        # Missing email
        response = client.post("/api/v1/auth/login", json={"password": "password"})
        assert response.status_code == 422

        # Missing password
        response = client.post("/api/v1/auth/login", json={"email": "test@example.com"})
        assert response.status_code == 422

        # Invalid email
        response = client.post("/api/v1/auth/login", json={"email": "not-an-email", "password": "password"})
        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()
