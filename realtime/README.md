# Realtime

## Purpose

Real-time infrastructure for live collaboration, presence, and event streaming. Built on WebSocket and Redis Streams.

## Responsibilities

- WebSocket server management
- Connection pooling
- Presence system
- Room/channel management
- Event broadcasting
- Message ordering guarantees
- Reconnection handling

## What Belongs Here

- WebSocket server
- Connection manager
- Presence tracker
- Room manager
- Event router

## What Must NEVER Belong Here

- Business logic (use services/)
- Database operations
- Authentication (delegate to auth)

## Dependencies

- `backend.websocket` - API routes
- `cache` - Redis Streams
- `auth` - Connection auth

## Future Phases

- Phase 10: Realtime implementation