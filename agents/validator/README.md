# Validator Agent

## Purpose

Validates workflow outputs, checks correctness, enforces quality gates, and ensures compliance with requirements.

## Responsibilities

- Output validation against specifications
- Code quality checks
- Security scanning
- Performance benchmarking
- Compliance verification
- Test generation and execution

## What Belongs Here

- Validator agent implementation
- Validation rule engine
- Quality gate definitions
- Prompt templates for validation

## What Must NEVER Belong Here

- Workflow execution
- Architecture decisions
- Database operations

## Dependencies

- `llm.providers` - LLM reasoning
- `agents.architect` - Receives architecture
- `workflows.executor` - Executes for validation

## Future Phases

- Phase 7: Validator implementation