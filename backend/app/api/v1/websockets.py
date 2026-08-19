"""WebSocket REST API router for v1 endpoints.

Exposes realtime WebSocket connection endpoint for workflow progress and agent updates:

- ``/ws/workflows/{workflow_id}``: Realtime WebSocket workflow subscription.
"""

from __future__ import annotations

from typing import Any

from fastapi import (
    APIRouter,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)

from app.core.config import get_settings
from app.security.exceptions import InvalidTokenError, TokenExpiredError
from app.security.jwt import JWTHelper
from app.workflows.websocket_manager import WebSocketManager
from app.workflows.workflow_engine import WorkflowEngine
from app.workflows.workflow_events import WorkflowEvent, WorkflowEventPublisher
from app.workflows.workflow_exceptions import WorkflowNotFoundError

websockets_router = APIRouter(prefix="/ws", tags=["websockets"])


def _authenticate_websocket_token(
    websocket: WebSocket, token_param: str | None
) -> dict[str, Any]:
    """Extract and validate JWT token from query parameter or authorization header.

    Args:
        websocket: The active WebSocket connection.
        token_param: Optional JWT token string from URL query parameter.

    Returns:
        Validated JWT claims dictionary.

    Raises:
        InvalidTokenError: If token is missing, expired, or invalid.
    """
    token = token_param
    if not token:
        auth_header = websocket.headers.get("authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header[7:].strip()

    if not token:
        raise InvalidTokenError("Authentication token is missing")

    jwt_helper = JWTHelper(settings=get_settings())
    return jwt_helper.decode_token(token)


@websockets_router.websocket("/workflows/{workflow_id}")
async def workflow_websocket_endpoint(
    websocket: WebSocket,
    workflow_id: str,
    token: str | None = Query(default=None),
) -> None:
    """Realtime WebSocket endpoint for workflow progress updates and heartbeat."""
    # 1. Authenticate WebSocket connection
    try:
        claims = _authenticate_websocket_token(websocket, token)
        if not claims.get("sub"):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except (InvalidTokenError, TokenExpiredError, Exception):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # 2. Resolve DI dependencies from app state
    container = websocket.app.state.container
    ws_manager: WebSocketManager = container.websocket_manager()
    event_publisher: WorkflowEventPublisher = container.workflow_event_publisher()
    engine: WorkflowEngine = container.workflow_engine()

    # 3. Verify workflow exists
    try:
        engine.load_workflow(workflow_id)
    except WorkflowNotFoundError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # 4. Connect and register listener
    await ws_manager.connect(workflow_id, websocket)

    background_tasks: set[Any] = set()

    def _on_event(event: WorkflowEvent) -> None:
        if event.workflow_id == workflow_id:
            import asyncio

            with contextlib.suppress(Exception):
                loop = asyncio.get_running_loop()
                task = loop.create_task(ws_manager.broadcast_event(workflow_id, event))
                background_tasks.add(task)
                task.add_done_callback(background_tasks.discard)

    import contextlib

    event_publisher.register_listener(_on_event)

    try:
        while True:
            raw_text = await websocket.receive_text()
            await ws_manager.handle_client_message(workflow_id, websocket, raw_text)
    except (WebSocketDisconnect, Exception) as exc:
        _ = exc
    finally:
        event_publisher.unregister_listener(_on_event)
        ws_manager.disconnect(workflow_id, websocket)
