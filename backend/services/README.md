# Services

## Purpose

The Service Layer - contains ALL business logic. This is the core of the application in Clean Architecture. Services orchestrate repositories, coordinate external systems, and enforce business rules.

## Responsibilities

- Implement business use cases
- Coordinate multiple repositories
- Manage transactions (unit of work)
- Integrate with external systems (LLM, payments, etc.)
- Emit domain events
- Enforce business invariants
- Transform data between layers

## What Belongs Here

- Service classes (stateless, singleton)
- Business rule validation
- Workflow orchestration
- Agent coordination
- LLM prompt engineering
- Payment processing logic
- Analytics aggregation

## What Must NEVER Belong Here

- HTTP concerns (request/response)
- Database query details (use repositories)
- Presentation formatting
- Infrastructure provisioning

## Dependencies

- `database.repositories` - Data access
- `llm.providers` - LLM access
- `llm.router` - Model routing
- `vector_db` - Vector search
- `cache` - Caching
- `payments` - Payment processing
- `auth` - Authorization checks

## Future Phases

- Phase 1: Base service infrastructure
- Phase 3: User, Organization services
- Phase 4: CRUD services
- Phase 5: LLM services
- Phase 7: Agent services
- Phase 8: Workflow execution services
- Phase 11: Billing services
- Phase 12: Analytics services