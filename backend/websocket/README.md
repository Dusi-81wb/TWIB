# WebSocket

## Purpose

Real-time bidirectional communication layer for live updates, collaborative features, and streaming responses.

## Responsibilities

- WebSocket connection lifecycle management
- Message routing and broadcasting
- Connection authentication
- Presence tracking
- Room/channel management
- Event streaming (workflow execution, agent output)

## What Belongs Here

- WebSocket route handlers
- Connection manager
- Message schemas
- Event types
- Room/channel logic

## What Must NEVER Belong Here

- Business logic (delegate to services)
- Database writes (delegate to services)
- LLM streaming (delegate to LLM services)

## Dependencies

- `backend.services` - Business logic
- `backend.schemas` - Message schemas
- `realtime` - Real-time infrastructure
- `auth` - Connection authentication

## Future Phases

- Phase 10: WebSocket implementation
- Phase 10: Presence system
- Phase 10: Collaborative editing