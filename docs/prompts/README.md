# Agent Prompts

## Purpose

Define the specification for each AI agent's prompts: purpose, inputs, outputs, and constraints.

## Responsibilities

- Document the intended behavior of each agent's system prompt
- Define inputs and expected outputs per agent
- Establish constraints for prompt design
- Track prompt status across development phases

## What Belongs Here

- One prompt specification file per agent
- Placeholder structure for future prompt content
- Consistency with the Agent contract in `AI_SPECIFICATION.md`

## What Must NEVER Belong Here

- Final production prompt text (unless a phase explicitly requires it)
- Implementation code
- Business logic

## Dependencies

- `docs/AI_SPECIFICATION.md` — agent lifecycle and contract
- `docs/architecture.md` — Agent Orchestrator and Context Manager layers

## Future Phases

- Fill in actual prompt content during Phase 6 (Agents)
- Version prompts alongside prompt templates in `llm/context`
