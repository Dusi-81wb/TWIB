# Core

## Purpose

Application bootstrap, lifespan management, and core infrastructure setup. The entry point that wires all layers together.

## Responsibilities

- FastAPI application factory
- Lifespan events (startup/shutdown)
- DI container initialization
- Middleware registration
- Router registration
- Exception handler registration
- Health check endpoints
- OpenAPI customization

## What Belongs Here

- `create_app()` factory function
- Lifespan context manager
- Application settings injection
- Root router inclusion

## What Must NEVER Belong Here

- Business logic
- Route handlers
- Database models
- Service implementations

## Dependencies

- All backend modules (for wiring)
- `backend.config` - Settings
- `backend.dependencies` - Container
- `backend.middleware` - Middleware
- `backend.api` - Routers
- `backend.exceptions` - Handlers

## Future Phases

- Phase 1: Application factory
- Phase 2: Auth middleware
- Phase 3: Database lifespan
- Phase 4: API routers
- Phase 5: LLM client lifespan
- Phase 10: WebSocket lifespan