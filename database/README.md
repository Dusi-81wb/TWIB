# Database

## Purpose

Database layer implementing the Repository pattern. Contains ORM models, repository implementations, migrations, and seed data.

## Responsibilities

- ORM model definitions (SQLAlchemy)
- Repository implementations
- Database migrations (Alembic)
- Seed data for environments
- Connection management
- Transaction handling

## What Belongs Here

- SQLAlchemy declarative models
- Repository classes
- Migration scripts
- Seed scripts
- Base repository interface

## What Must NEVER Belong Here

- Business logic (use services/)
- HTTP concerns
- LLM calls
- Presentation logic

## Dependencies

- `sqlalchemy` 2.0+
- `alembic`
- `asyncpg` driver
- `backend.config` - Database URL

## Future Phases

- Phase 3: Database layer