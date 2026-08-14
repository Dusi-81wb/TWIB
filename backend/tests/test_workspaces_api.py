"""Tests for Workspace API endpoints."""

import pytest
from typing import Any, cast
from fastapi.testclient import TestClient

from app.core.settings import ApplicationSettings
from app.security import JWTHelper
from app.dependencies import get_workspace_service, get_authorization_service
from app.domain.exceptions import EntityNotFound

@pytest.fixture
def auth_headers() -> dict[str, str]:
    jwt_helper = JWTHelper(ApplicationSettings())
    token = jwt_helper.create_access_token(
        {"sub": "00000000-0000-0000-0000-000000000001", "email": "test@example.com"}
    )
    return {"Authorization": f"Bearer {token}"}

class MockAuthorizationService:
    async def has_workspace_access(self, user_id: str, workspace_id: str) -> bool:
        return True

class MockWorkspaceService:
    async def get_members(self, workspace_id: str) -> Any:
        raise EntityNotFound("Workspace not found")

def test_list_workspace_members_not_found(client: TestClient, auth_headers: dict[str, str]) -> None:
    app = cast(Any, client.app)
    app.dependency_overrides[get_workspace_service] = lambda: MockWorkspaceService()
    app.dependency_overrides[get_authorization_service] = lambda: MockAuthorizationService()

    try:
        resp = client.get("/api/v1/workspaces/test-ws-123/members", headers=auth_headers)
        assert resp.status_code == 404
        assert resp.json()["error"]["message"] == "Workspace not found"
    finally:
        app.dependency_overrides.pop(get_workspace_service, None)
        app.dependency_overrides.pop(get_authorization_service, None)
