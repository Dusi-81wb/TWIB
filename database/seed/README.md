# Database Seed

## Purpose

Seed data scripts for initializing databases in different environments (development, testing, staging, production).

## Responsibilities

- Reference data (roles, permissions, defaults)
- Development fixtures
- Test data generators
- Production bootstrap data

## What Belongs Here

- Seed scripts
- Data factories
- Fixture definitions
- Environment-specific seed configs

## What Must NEVER Belong Here

- Migration scripts (use migrations/)
- Model definitions
- Business logic

## Dependencies

- `database.repositories` - Data insertion
- `database.models` - Model access

## Future Phases

- Phase 3: Seed data