# Vector Database

## Purpose

Vector database integration for semantic search, embeddings storage, and similarity-based retrieval. Uses Qdrant as the primary vector store.

## Responsibilities

- Vector collection management
- Embedding upsert and query
- Filtered similarity search
- Hybrid search (vector + metadata)
- Collection optimization
- Snapshot/backup

## What Belongs Here

- Qdrant client wrapper
- Collection schemas
- Search service
- Index management

## What Must NEVER Belong Here

- Embedding generation (use llm/embeddings)
- Business logic
- Workflow execution

## Dependencies

- `qdrant-client`
- `llm.embeddings` - Embedding generation
- `cache` - Query caching

## Future Phases

- Phase 5: Vector DB integration