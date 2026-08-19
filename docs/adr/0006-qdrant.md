# ADR-0006 Qdrant

## Status

Accepted

## Context

TWIB requires a vector database for semantic memory, knowledge retrieval, and RAG workflows. The chosen store must support filtered similarity search, horizontal scaling, and self-hosted deployment, and must integrate cleanly behind an abstraction.

## Decision

Use Qdrant as the vector database.

- Purpose-built for vector similarity search with HNSW indexing
- Supports filtered vector search combining metadata and vectors
- Easy Docker/Kubernetes deployment and horizontal scaling
- Mature Python client for async integration
- Embedded behind a vector store abstraction, keeping it replaceable

## Alternatives Considered

- Pinecone: managed-only, vendor lock-in, higher cost
- Weaviate: heavier, more complex operations
- Milvus: complex deployment and operations
- pgvector: simpler, but limited at production vector scale

## Consequences

- Efficient semantic retrieval at scale
- Collection management and snapshots add operational tasks
- Requires consistent embedding pipelines from `llm/embeddings`
- Provider remains swappable via the abstraction layer
