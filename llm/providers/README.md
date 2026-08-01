# LLM Providers

## Purpose

Concrete implementations for each LLM provider (OpenAI, Anthropic, Ollama, etc.) conforming to the unified provider interface.

## Responsibilities

- Provider-specific API clients
- Request/response transformation
- Streaming support
- Error mapping to unified exceptions
- Model capability metadata
- Authentication handling

## What Belongs Here

- Provider adapter classes
- Model configuration
- Streaming handlers
- Provider-specific optimizations

## What Must NEVER Belong Here

- Routing logic (use router/)
- Business logic
- Database operations

## Dependencies

- `llm` - Provider interface
- Provider SDKs
- `backend.config` - API keys

## Future Phases

- Phase 5: OpenAI, Anthropic, Ollama providers