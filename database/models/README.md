# Database Models

## Purpose

SQLAlchemy ORM models representing database tables. Pure data structures with no business logic.

## Responsibilities

- Table definitions
- Column types and constraints
- Relationships (foreign keys)
- Indexes
- Model mixins (timestamp, soft delete)

## What Belongs Here

- Declarative model classes
- Association tables
- Enum definitions
- Custom types

## What Must NEVER Belong Here

- Business logic
- Query logic (use repositories)
- Validation (use schemas)
- Event handlers

## Dependencies

- `sqlalchemy.orm`
- `database` - Base model

## Future Phases

- Phase 3: Model definitions