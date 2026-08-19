# Researcher Agent

## Purpose

Gathers external information, researches best practices, fetches documentation, and discovers relevant APIs/services for workflow construction.

## Responsibilities

- Web search and scraping
- API documentation retrieval
- Best practice research
- Technology evaluation
- Competitive analysis
- Knowledge synthesis

## What Belongs Here

- Researcher agent implementation
- Search integrations
- Documentation parsers
- Knowledge base management
- Prompt templates for research

## What Must NEVER Belong Here

- Workflow execution
- Architecture decisions
- Database operations (except caching research)

## Dependencies

- `llm.providers` - LLM reasoning
- `llm.embeddings` - Semantic search
- `vector_db` - Knowledge storage
- `cache` - Research caching

## Future Phases

- Phase 7: Researcher implementation