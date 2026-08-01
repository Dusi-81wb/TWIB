# ADR-0003 PostgreSQL

## Status

Accepted

## Context

TWIB requires a relational database for transactional business data (users, organizations, workflows, executions, billing) with strong consistency, JSON support, and enterprise-grade reliability.

## Decision

Use PostgreSQL (via SQLAlchemy 2.0 async ORM) as the primary relational database.

- ACID transactions for billing and workflow state
- JSONB for flexible structured data (workflow graphs, prompts)
- Mature async driver (asyncpg) that fits the async backend
- Full-text search and rich indexing
- Managed service availability across clouds (RDS, Cloud SQL)
- Abstraction via the Repository pattern keeps it replaceable

## Alternatives Considered

- MySQL: weaker JSON and full-text capabilities
- SQLite: not production-ready for multi-tenant scale
- NoSQL (MongoDB/DynamoDB): not the right fit for transactional core entities
- Raw SQL: loses ORM, typing, and migration benefits

## Consequences

- Strong consistency for business-critical data
- Repository pattern isolates services from SQLAlchemy specifics
- Migration overhead managed by Alembic
- Horizontal scaling requires read replicas at production scale
