# LLM

## Purpose

Abstraction layer for all Large Language Model interactions. Provides unified interface across providers, intelligent routing, and context management.

## Responsibilities

- Provider abstraction (unified interface)
- Model routing and selection
- Embedding generation
- Token counting and optimization
- Context window management
- Cost tracking
- Rate limiting

## What Belongs Here

- Provider interfaces and implementations
- Router logic
- Embedding service
- Tokenizer utilities
- Context managers
- Usage tracking

## What Must NEVER Belong Here

- Business logic (use services/)
- Agent implementations (use agents/)
- Workflow execution (use workflows/)
- Database operations

## Dependencies

- Provider SDKs (openai, anthropic, etc.)
- `cache` - Response caching
- `vector_db` - Embedding storage

## Future Phases

- Phase 5: Provider abstractions
- Phase 6: Model router