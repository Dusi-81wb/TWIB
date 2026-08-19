# Database Migrations

## Purpose

Alembic migration scripts for schema evolution. Version-controlled database schema changes.

## Responsibilities

- Migration scripts (upgrade/downgrade)
- Schema versioning
- Data migrations
- Environment-specific migrations

## What Belongs Here

- Alembic `env.py` configuration
- Migration scripts (`versions/`)
- Migration utilities

## What Must NEVER Belong Here

- Model definitions (use models/)
- Application code
- Seed data (use seed/)

## Dependencies

- `alembic`
- `database.models` - Target metadata

## Future Phases

- Phase 3: Migration setup