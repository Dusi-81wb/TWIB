# ADR-0002 FastAPI

## Status

Accepted

## Context

The backend must handle concurrent async operations (LLM calls, workflow execution, WebSocket) and produce automatic API documentation. The framework must support Clean Architecture, dependency injection, and strict typing.

## Decision

Use FastAPI (Python 3.11+) as the web framework for the backend API layer.

- Async-native with full asyncio support
- Automatic OpenAPI/Swagger documentation from Pydantic schemas
- Native dependency injection (`Depends`) that complements the DI container
- First-class WebSocket support for realtime features
- Type-safe request validation and response serialization

## Alternatives Considered

- Django: monolithic, sync-first, heavier for async-heavy workloads
- Flask: no native async or DI, lacks structure for enterprise modules
- Litestar/Starlette: smaller ecosystem, less battle-tested

## Consequences

- High performance for I/O-bound workloads (LLM calls, DB, WS)
- Automatic and always-current API docs
- Team must follow async conventions to avoid blocking the event loop
- Python-based, aligning with the AI/ML ecosystem
