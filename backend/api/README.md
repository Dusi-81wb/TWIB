# Backend API

## Purpose

Defines HTTP route handlers (endpoints) for the REST API. This is the API layer in Clean Architecture - thin delegators to services.

## Responsibilities

- Define route paths, methods, and parameters
- Validate request payloads via Pydantic schemas
- Delegate to service layer for business logic
- Return standardized responses
- Handle HTTP-specific concerns (status codes, headers)

## What Belongs Here

- FastAPI router instances
- Route handler functions (async def)
- Request/response schema imports
- Dependency injection for services
- OpenAPI documentation metadata

## What Must NEVER Belong Here

- Business logic (belongs in services)
- Database queries (belongs in repositories)
- Direct LLM calls (belongs in services/llm)
- Complex data transformations
- Authentication logic (use middleware/dependencies)

## Dependencies

- `backend.services` - Business logic
- `backend.schemas` - Request/response models
- `backend.dependencies` - Service injection
- `backend.exceptions` - Error handling

## Future Phases

- Phase 4: REST API implementation