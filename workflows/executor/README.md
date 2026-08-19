# Workflow Executor

## Purpose

The execution engine that runs workflow graphs. Handles node scheduling, state transitions, error handling, retries, and observability.

## Responsibilities

- Workflow instantiation
- Node scheduling (topological + dynamic)
- State management (persistent)
- Checkpointing and recovery
- Retry policies
- Timeout enforcement
- Event emission (started, completed, failed, node events)
- Distributed execution support

## What Belongs Here

- Executor class
- Scheduling algorithms
- State machine
- Checkpoint manager
- Event system
- Execution context

## What Must NEVER Belong Here

- Node implementations (use nodes/)
- Graph algorithms (use graph/)
- Persistence details (use database/repositories)

## Dependencies

- `workflows.graph` - Graph structures
- `workflows.nodes` - Node execution
- `workflows.edges` - Routing
- `workflows.memory` - State storage
- `database.repositories` - Persistence
- `realtime` - Live events
- `analytics` - Execution metrics

## Future Phases

- Phase 8: Executor implementation