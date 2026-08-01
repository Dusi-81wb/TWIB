# Workflow Nodes

## Purpose

Node type definitions and base classes for workflow execution nodes. Each node type encapsulates a unit of work.

## Responsibilities

- Base node abstract class
- Built-in node types (LLM, Tool, Condition, Loop, Parallel, Human)
- Node input/output schemas
- Node configuration validation
- Execution context management

## What Belongs Here

- Node base class
- Node type registry
- Standard node implementations
- Node schema definitions
- Custom node extension point

## What Must NEVER Belong Here

- Execution engine (use executor/)
- Graph algorithms (use graph/)
- Agent implementations (use agents/)

## Dependencies

- `workflows.graph` - Graph structures
- `llm.providers` - For LLM nodes
- `agents` - For agent nodes
- `backend.schemas` - Input/output validation

## Future Phases

- Phase 8: Node type implementations