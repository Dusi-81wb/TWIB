# Schemas

## Purpose

Pydantic models defining API contracts (request/response), data transfer objects, and validation rules. The single source of truth for data shapes crossing layer boundaries.

## Responsibilities

- Define request payload validation
- Define response serialization
- Document API contracts (OpenAPI)
- Shared types between frontend/backend
- Input sanitization

## What Belongs Here

- Pydantic `BaseModel` classes
- Request/response models per endpoint
- Enum definitions
- Custom validators
- Type aliases

## What Must NEVER Belong Here

- Business logic
- Database models (ORM)
- Service implementations
- Database queries

## Dependencies

- `pydantic`
- `typing` extensions
- Shared with frontend via code generation or manual sync

## Future Phases

- Phase 1: Base schemas, error responses
- Phase 2: Auth schemas
- Phase 3: Entity schemas
- Phase 4: All API schemas
- Phase 5: LLM schemas
- Phase 7: Agent schemas
- Phase 8: Workflow schemas