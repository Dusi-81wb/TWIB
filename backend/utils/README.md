# Utils

## Purpose

Pure, stateless utility functions with no external dependencies. Reusable helpers that don't belong to any specific domain.

## Responsibilities

- String manipulation
- Date/time formatting
- Data serialization
- Cryptographic helpers
- Validation helpers
- Collection utilities
- Async utilities

## What Belongs Here

- Pure functions (no side effects)
- Type-safe helpers
- Well-tested utilities
- Generic algorithms

## What Must NEVER Belong Here

- Business logic
- Database access
- HTTP calls
- Configuration access
- Logging (except pure formatting)
- State mutation

## Dependencies

- Python standard library only
- Zero external dependencies

## Future Phases

- Phase 1: Core utilities
- Phase 3: Database utilities
- Phase 5: LLM utilities (token counting, etc.)
- Phase 8: Workflow utilities