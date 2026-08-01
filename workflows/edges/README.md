# Workflow Edges

## Purpose

Edge type definitions controlling flow between nodes including conditional routing, parallel splits, and error handling paths.

## Responsibilities

- Base edge abstract class
- Edge types (Sequence, Condition, Parallel, Error, Compensation)
- Routing logic evaluation
- Edge configuration validation
- Branch merging strategies

## What Belongs Here

- Edge base class
- Edge type implementations
- Condition evaluation engine
- Routing strategies

## What Must NEVER Belong Here

- Node implementations (use nodes/)
- Execution engine (use executor/)
- Graph algorithms (use graph/)

## Dependencies

- `workflows.graph` - Graph structures
- `workflows.nodes` - Node references
- `backend.schemas` - Condition schemas

## Future Phases

- Phase 8: Edge type implementations