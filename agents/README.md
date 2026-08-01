# Agents

## Purpose

AI Agent implementations - specialized autonomous agents that collaborate to build workflows. Each agent has a distinct role in the workflow generation pipeline.

## Responsibilities

- Define agent interfaces and base classes
- Implement specialized agent behaviors
- Manage agent-to-agent communication
- Coordinate multi-agent workflows
- Handle agent state and memory

## What Belongs Here

- Base agent abstract class
- Individual agent implementations
- Agent communication protocols
- Prompt templates per agent
- Agent configuration

## What Must NEVER Belong Here

- HTTP endpoints
- Database models
- Workflow execution engine
- LLM provider implementations (use llm/providers)

## Dependencies

- `llm.providers` - LLM access
- `llm.router` - Model selection
- `workflows` - Workflow structures
- `backend.services` - Business logic coordination

## Future Phases

- Phase 7: All agent implementations