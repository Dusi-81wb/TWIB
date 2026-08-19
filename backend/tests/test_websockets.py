"""Tests for Realtime Events and WebSocket endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.core.settings import ApplicationSettings
from app.security import JWTHelper
from app.workflows.workflow_events import (
    WorkflowEvent,
    WorkflowEventPublisher,
    WorkflowEventType,
)


@pytest.fixture
def auth_token() -> str:
    jwt_helper = JWTHelper(ApplicationSettings())
    return jwt_helper.create_access_token(
        {"sub": "00000000-0000-0000-0000-000000000001", "email": "test@example.com"}
    )


@pytest.mark.asyncio
async def test_workflow_event_publisher() -> None:
    publisher = WorkflowEventPublisher()

    received_events: list[WorkflowEvent] = []
    publisher.register_listener(lambda ev: received_events.append(ev))

    event = WorkflowEvent(
        workflow_id="wf-123",
        event_type=WorkflowEventType.WORKFLOW_STARTED,
        message="Workflow execution started",
    )
    publisher.publish(event)

    assert len(received_events) == 1
    assert received_events[0].workflow_id == "wf-123"
    assert received_events[0].event_type == "workflow.started"


def test_websocket_endpoint_unauthenticated(client: TestClient) -> None:
    # Attempting WS connection without auth token should close connection
    from starlette.websockets import WebSocketDisconnect

    with (
        pytest.raises((WebSocketDisconnect, Exception)),
        client.websocket_connect("/api/v1/ws/workflows/non-existent"),
    ):
        pass


def test_websocket_endpoint_flow(client: TestClient, auth_token: str) -> None:
    # 1. Create a workflow via REST API first
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = client.post(
        "/api/v1/workflows",
        json={"workflow_name": "WS Test WF", "user_request": "Test WS"},
        headers=headers,
    )
    assert resp.status_code == 201
    wf_id = resp.json()["workflow_id"]

    # 2. Connect via WebSocket with token query param
    ws_url = f"/api/v1/ws/workflows/{wf_id}?token={auth_token}"
    with client.websocket_connect(ws_url) as websocket:
        # Send heartbeat ping
        websocket.send_text("ping")
        response_text = websocket.receive_text()
        assert "pong" in response_text
