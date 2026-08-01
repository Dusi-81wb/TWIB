# Backend

## Purpose

The FastAPI Python application serving as the API layer and orchestration layer in Clean Architecture. Contains all business logic, data access, and external integrations.

## Responsibilities

- Expose RESTful API endpoints
- Manage WebSocket connections
- Orchestrate business workflows via services
- Coordinate AI agents
- Execute workflow graphs
- Manage LLM provider interactions
- Handle authentication & authorization
- Persist and retrieve data

## What Belongs Here

- API route definitions (thin, delegation only)
- Service layer (business logic)
- Repository implementations
- Database models
- LLM provider adapters
- Agent implementations
- Workflow engine
- Configuration management
- Middleware
- Exception handling
- Dependency injection container

## What Must NEVER Belong Here

- Frontend code
- Presentation logic (HTML templates, etc.)
- Infrastructure provisioning code
- CI/CD pipeline definitions

## Dependencies

- PostgreSQL database
- Redis/Valkey cache
- Qdrant vector database
- LLM provider APIs
- Authentication provider
- Payment provider (Stripe)

## Future Phases

- Phase 1: Foundation setup
- Phase 2: Authentication
- Phase 3: Database layer
- Phase 4: REST APIs
- Phase 5: LLM Integration
- Phase 6: Model Router
- Phase 7: Agent Framework
- Phase 8: Workflow Engine