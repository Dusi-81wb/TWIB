"""Integration tests for the Workspaces API endpoints."""

from __future__ import annotations

from typing import Any, cast

from fastapi.testclient import TestClient

from app.dependencies import (
    get_authorization_service,
    get_current_user_claims,
    get_workspace_service,
)
from app.domain.exceptions import BusinessRuleViolation


class MockAuthorizationService:
    """Mock AuthorizationService for API integration testing."""

    async def has_workspace_access(
        self,
        user_id: str,
        workspace_id: str,
        required_role: Any = None,
    ) -> bool:
        """Mock has_workspace_access always returns True."""
        return True


class MockWorkspaceService:
    """Mock WorkspaceService for testing update_workspace."""

    async def update_workspace(
        self,
        workspace_id: str,
        name: str | None = None,
        slug: str | None = None,
        description: str | None = None,
        status: str | None = None,
    ) -> Any:
        """Mock update_workspace raising BusinessRuleViolation."""
        raise BusinessRuleViolation("Domain invariant violated")


def test_update_workspace_business_rule_violation(client: TestClient) -> None:
    """Test PATCH /api/v1/workspaces/{workspace_id} handles BusinessRuleViolation."""
    mock_workspace_service = MockWorkspaceService()
    mock_authz_service = MockAuthorizationService()

    app = cast(Any, client.app)

    # Store old overrides
    old_overrides = dict(app.dependency_overrides)

    app.dependency_overrides[get_workspace_service] = lambda: mock_workspace_service
    app.dependency_overrides[get_authorization_service] = lambda: mock_authz_service
    app.dependency_overrides[get_current_user_claims] = lambda: {"sub": "user_1", "role": "admin"}

    try:
        payload = {
            "name": "Invalid Workspace Update",
        }
        response = client.patch("/api/v1/workspaces/ws_1", json=payload)

        assert response.status_code == 400
        data = response.json()
        assert "Domain invariant violated" in data["error"]["message"]
    finally:
        # Restore old overrides to not pollute other tests
        app.dependency_overrides = old_overrides
