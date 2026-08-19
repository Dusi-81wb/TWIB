# Supervisor Agent

## Purpose

Orchestrates multi-agent collaboration, manages agent lifecycle, coordinates handoffs, and ensures workflow generation quality.

## Responsibilities

- Agent coordination and scheduling
- Handoff management between agents
- Conflict resolution
- Quality gate enforcement
- Progress tracking
- Failure recovery
- Human-in-the-loop escalation

## What Belongs Here

- Supervisor agent implementation
- Orchestration engine
- Agent registry
- State machine for workflow generation
- Prompt templates for supervision

## What Must NEVER Belong Here

- Individual agent logic (delegated to agents)
- Workflow execution (delegated to workflows.executor)
- Database operations

## Dependencies

- All agent modules
- `llm.providers` - LLM reasoning
- `workflows` - Workflow structures
- `backend.services` - Business coordination

## Future Phases

- Phase 7: Supervisor implementation