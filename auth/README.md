# Auth

## Purpose

Authentication and authorization infrastructure. Integrates with external identity providers and manages access control for the platform.

## Responsibilities

- Identity provider integration (Auth0, Clerk, etc.)
- JWT validation and claims extraction
- Role-based access control (RBAC)
- API key management
- Session management
- Permission evaluation
- Audit logging

## What Belongs Here

- Auth provider adapters
- JWT middleware
- RBAC policy definitions
- Permission decorators
- API key service
- Auth schemas

## What Must NEVER Belong Here

- User management UI (frontend/)
- Business logic (use services/)
- Database models (use database/models)

## Dependencies

- External auth provider SDKs
- `backend.middleware` - Auth middleware
- `backend.schemas` - Auth schemas
- `database.repositories` - User/org persistence

## Future Phases

- Phase 2: Auth implementation