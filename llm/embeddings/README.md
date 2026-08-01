# LLM Embeddings

## Purpose

Embedding generation and management for semantic search, memory, and similarity operations across the platform.

## Responsibilities

- Embedding model abstraction
- Batch embedding generation
- Dimension management
- Similarity computation
- Embedding caching
- Model versioning

## What Belongs Here

- Embedding service
- Provider-specific embedding adapters
- Vector operations
- Cache integration

## What Must NEVER Belong Here

- Vector database operations (use vector_db/)
- Business logic
- Workflow logic

## Dependencies

- `llm.providers` - Embedding models
- `vector_db` - Storage
- `cache` - Embedding cache

## Future Phases

- Phase 5: Embedding service