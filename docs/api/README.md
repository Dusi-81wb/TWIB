# API Documentation

## Purpose

Document the planned TWIB API surface: endpoints, authentication, and conventions.

## Responsibilities

- Define the planned REST and WebSocket API contracts
- Document authentication requirements per resource
- Provide a stable reference for frontend and backend teams
- Track the status of each API group

## What Belongs Here

- API documentation per resource group (auth, users, workflows, etc.)
- Planned endpoint lists and authentication notes
- WebSocket protocol documentation

## What Must NEVER Belong Here

- Implemented endpoint logic (that is code, not docs)
- Database schemas
- Business logic

## Dependencies

- `docs/architecture.md` — layer responsibilities for the API layer
- `backend/schemas/` — future source of truth for request/response models
- `docs/folder_structure.md` — API route structure

## Future Phases

- Expand endpoint documentation as Phase 4 (REST API) is implemented
- Document schemas and error responses in detail
