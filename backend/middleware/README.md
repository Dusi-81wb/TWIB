# Middleware

## Purpose

Cross-cutting concerns that wrap request/response processing. Implements the middleware layer in Clean Architecture.

## Responsibilities

- Request/response logging
- Authentication validation
- Rate limiting
- CORS handling
- Error formatting
- Request ID generation
- Metrics collection
- Security headers

## What Belongs Here

- ASGI middleware classes
- FastAPI middleware functions
- Custom middleware for auth, logging, metrics
- Exception handlers

## What Must NEVER Belong Here

- Business logic
- Database operations
- LLM calls
- Route definitions

## Dependencies

- `backend.exceptions` - Error types
- `backend.utils` - Logging, metrics helpers
- `auth` - Token validation

## Future Phases

- Phase 1: Logging, request ID, CORS
- Phase 2: Authentication middleware
- Phase 12: Metrics middleware
- Phase 14: Security headers, rate limiting