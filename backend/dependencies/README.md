# Dependencies

## Purpose

Dependency Injection container and provider registrations. Centralizes object graph construction for the application.

## Responsibilities

- Define service interfaces (protocols)
- Register concrete implementations
- Manage object lifecycles (singleton, request, transient)
- Provide override mechanism for testing
- Wire application components

## What Belongs Here

- `dependency-injector` containers
- Provider definitions
- Interface/protocol definitions
- Factory functions
- Configuration injection

## What Must NEVER Belong Here

- Business logic
- Database models
- Route handlers
- Schema definitions

## Dependencies

- `backend.services` - Service implementations
- `backend.repositories` - Repository implementations
- `llm.providers` - LLM provider implementations
- `database.repositories` - Database repositories
- `config` - Configuration values

## Future Phases

- Phase 1: Container setup
- Phase 3: Repository wiring
- Phase 5: LLM provider wiring
- Phase 7: Agent wiring
- Phase 8: Workflow engine wiring