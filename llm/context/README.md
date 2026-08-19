# LLM Context

## Purpose

Context window management for multi-turn conversations, agent memory, and RAG (Retrieval-Augmented Generation) workflows.

## Responsibilities

- Context assembly (system, history, RAG, tools)
- Window sliding strategies
- Priority-based inclusion
- Context compression
- Token budget allocation

## What Belongs Here

- Context builder
- Window management strategies
- Compression algorithms
- Budget allocators

## What Must NEVER Belong Here

- LLM calls
- Vector search (use vector_db/)
- Business logic

## Dependencies

- `llm.tokenizer` - Token counting
- `llm.embeddings` - RAG embeddings
- `vector_db` - Retrieval
- `workflows.memory` - Conversation history

## Future Phases

- Phase 5: Context management