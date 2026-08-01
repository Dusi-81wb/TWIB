# Documentation Agent

## Purpose

Automatically generates comprehensive documentation for workflows including technical specs, user guides, API docs, and architecture diagrams.

## Responsibilities

- Technical specification generation
- User guide creation
- API documentation
- Architecture diagram generation (Mermaid)
- Change log maintenance
- Multi-format output (Markdown, HTML, PDF)

## What Belongs Here

- Documentation agent implementation
- Template engine for docs
- Diagram generators
- Format converters
- Prompt templates for documentation

## What Must NEVER Belong Here

- Workflow execution
- Architecture decisions
- Database operations

## Dependencies

- `llm.providers` - LLM generation
- `agents.architect` - Architecture input
- `agents.validator` - Validation results

## Future Phases

- Phase 7: Documentation agent implementation