# Workflows

## Purpose

Workflow engine - the core execution system that runs generated workflows as directed graphs with state management, persistence, and monitoring.

## Responsibilities

- Graph data structures and algorithms
- Node and edge type definitions
- Workflow execution engine
- State persistence and recovery
- Template system for reusable workflows
- Memory management for long-running workflows

## What Belongs Here

- Graph implementation (nodes, edges, traversal)
- Node type registry
- Executor implementation
- State management
- Template definitions
- Memory stores

## What Must NEVER Belong Here

- Agent implementations (use agents/)
- LLM provider calls (use llm/)
- HTTP endpoints
- Database models (use database/models)

## Dependencies

- `agents` - Agent execution nodes
- `llm.providers` - LLM calls within nodes
- `database.repositories` - Persistence
- `vector_db` - Semantic memory
- `cache` - Execution caching
- `realtime` - Live updates

## Future Phases

- Phase 8: Complete workflow engine