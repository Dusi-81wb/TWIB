# Exceptions

## Purpose

Custom exception hierarchy for the application. Provides structured error handling with proper HTTP status codes and error codes.

## Responsibilities

- Define application-specific exceptions
- Map exceptions to HTTP responses
- Provide error codes for client handling
- Enable structured error logging
- Support internationalization

## What Belongs Here

- Base exception class
- Domain-specific exceptions (NotFound, ValidationError, BusinessRuleViolation, etc.)
- HTTP status code mapping
- Error code constants
- Exception handlers for FastAPI

## What Must NEVER Belong Here

- Business logic
- Database operations
- Logging implementation (use utils)

## Dependencies

- `fastapi` for HTTPException
- `backend.utils` for logging

## Future Phases

- Phase 1: Base exception hierarchy
- Phase 2: Auth exceptions
- Phase 3: Database exceptions
- Phase 4: API exceptions
- Phase 5: LLM exceptions
- Phase 7: Agent exceptions
- Phase 8: Workflow exceptions