# Database Repositories

## Purpose

Repository implementations providing data access abstraction. Each repository handles one aggregate root.

## Responsibilities

- CRUD operations
- Query methods (filter, pagination, sorting)
- Transaction management
- Aggregate persistence
- Domain event publishing

## What Belongs Here

- Repository classes
- Query builders
- Base repository abstract class
- Unit of work pattern

## What Must NEVER Belong Here

- Business logic (use services/)
- HTTP concerns
- Model definitions (use models/)

## Dependencies

- `database.models` - ORM models
- `database` - Base repository

## Future Phases

- Phase 3: Repository implementations