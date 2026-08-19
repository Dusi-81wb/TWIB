"""WebSocket Connection Manager implementation.

Manages active client WebSocket connections per workflow_id, connection lifecycles,
heartbeats, and realtime event broadcasting.
"""

from __future__ import annotations

import json
from collections import defaultdict

from fastapi import WebSocket

from app.workflows.workflow_events import WorkflowEvent


class WebSocketManager:
    """Manager for tracking and broadcasting to active WebSocket client connections."""

    def __init__(self) -> None:
        """Initialize WebSocketManager."""
        self._active_connections: dict[str, list[WebSocket]] = defaultdict(list)

    @property
    def connection_counts(self) -> dict[str, int]:
        """Return count of active socket connections per workflow_id."""
        return {
            wf_id: len(sockets) for wf_id, sockets in self._active_connections.items()
        }

    async def connect(self, workflow_id: str, websocket: WebSocket) -> None:
        """Accept WebSocket connection and register under workflow_id."""
        await websocket.accept()
        if websocket not in self._active_connections[workflow_id]:
            self._active_connections[workflow_id].append(websocket)

    def disconnect(self, workflow_id: str, websocket: WebSocket) -> None:
        """Remove WebSocket connection and clean up empty map entries."""
        if workflow_id in self._active_connections:
            if websocket in self._active_connections[workflow_id]:
                self._active_connections[workflow_id].remove(websocket)
            if not self._active_connections[workflow_id]:
                del self._active_connections[workflow_id]

    async def broadcast_event(self, workflow_id: str, event: WorkflowEvent) -> None:
        """Broadcast a WorkflowEvent to all active sockets connected to workflow_id."""
        sockets = list(self._active_connections.get(workflow_id, []))
        if not sockets:
            return

        payload_json = event.model_dump_json()
        dead_sockets: list[WebSocket] = []

        for socket in sockets:
            try:
                await socket.send_text(payload_json)
            except Exception:
                dead_sockets.append(socket)

        for socket in dead_sockets:
            self.disconnect(workflow_id, socket)

    async def handle_client_message(
        self, workflow_id: str, websocket: WebSocket, raw_message: str
    ) -> None:
        """Process incoming client message (e.g. heartbeat ping)."""
        import contextlib

        msg_str = raw_message.strip()
        if msg_str in ("ping", '{"type":"ping"}', '{"type": "ping"}'):
            await websocket.send_text(json.dumps({"type": "pong"}))
        else:
            with contextlib.suppress(Exception):
                data = json.loads(msg_str)
                if isinstance(data, dict) and data.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
