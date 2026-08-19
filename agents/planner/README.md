# Planner Agent

## Purpose

Decomposes high-level goals into executable task sequences. The entry point for workflow generation.

## Responsibilities

- Goal analysis and decomposition
- Task dependency identification
- Execution order optimization
- Resource requirement estimation
- Risk assessment

## What Belongs Here

- Planner agent implementation
- Planning algorithms
- Task graph generation
- Prompt templates for planning

## What Must NEVER Belong Here

- Workflow execution
- Code generation
- Database operations

## Dependencies

- `llm.providers` - LLM reasoning
- `workflows.graph` - Task graph structures

## Future Phases

- Phase 7: Planner implementation