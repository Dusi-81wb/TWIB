# Workflow Memory

## Purpose

State management for long-running workflows including checkpoint storage, variable scoping, and semantic memory for context retention across executions.

## Responsibilities

- Workflow state persistence
- Variable scope management (global, node, execution)
- Checkpoint serialization
- Semantic memory (vector-based context)
- Memory garbage collection
- Memory querying for agents

## What Belongs Here

- Memory store interfaces
- State serialization
- Checkpoint manager
- Semantic memory integration
- Scope resolvers

## What Must NEVER Belong Here

- Execution logic (use executor/)
- Node implementations
- Database models (use database/models)

## Dependencies

- `database.repositories` - State persistence
- `vector_db` - Semantic memory
- `cache` - Hot state caching
- `llm.embeddings` - Memory embeddings

## Future Phases

- Phase 8: Memory implementation