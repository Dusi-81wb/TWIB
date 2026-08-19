"""LLM abstraction package alias.

Re-exports LLM provider interfaces and models from :mod:`app.infrastructure.llm`.
"""

from app.infrastructure.llm import (
    AsyncStreamWrapper,
    AuthenticationError,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    CompletionUsage,
    ContextWindowExceededError,
    Conversation,
    InvalidModelError,
    LLMProvider,
    LLMProviderError,
    LLMProviderFactory,
    LLMProviderRegistry,
    MessageRole,
    ModelInfo,
    OllamaProvider,
    OpenAIProvider,
    ProviderError,
    ProviderUnavailableError,
    RateLimitError,
    StreamChunk,
    get_default_registry,
)

__all__ = [
    "AsyncStreamWrapper",
    "AuthenticationError",
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
    "CompletionUsage",
    "ContextWindowExceededError",
    "Conversation",
    "InvalidModelError",
    "LLMProvider",
    "LLMProviderError",
    "LLMProviderFactory",
    "LLMProviderRegistry",
    "MessageRole",
    "ModelInfo",
    "OllamaProvider",
    "OpenAIProvider",
    "ProviderError",
    "ProviderUnavailableError",
    "RateLimitError",
    "StreamChunk",
    "get_default_registry",
]
