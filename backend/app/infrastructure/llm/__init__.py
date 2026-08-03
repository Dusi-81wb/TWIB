"""LLM Provider abstraction package.

Exposes provider-independent interfaces, models, exceptions, and types:

- :class:`.LLMProvider`: Abstract base class for LLM providers.
- :class:`.ChatMessage`: Unified chat message representation.
- :class:`.MessageRole`: Conversation author role enumeration.
- :class:`.ChatRequest`: Completion request payload.
- :class:`.ChatResponse`: Completion response object.
- :class:`.StreamChunk`: Streaming content delta chunk.
- :class:`.CompletionUsage`: Token usage metrics.
- :class:`.ModelInfo`: Model metadata and capabilities.
- :class:`.LLMProviderError`: Base exception for LLM provider errors.
- :class:`.RateLimitError`: Exception raised on rate limits.
- :class:`.InvalidModelError`: Exception raised for invalid models.
- :class:`.AuthenticationError`: Exception raised for auth failures.
- :class:`.ContextWindowExceededError`: Exception raised for context overflow.
- :class:`.ProviderUnavailableError`: Exception raised when provider is down.
"""

from app.infrastructure.llm.conversation import Conversation
from app.infrastructure.llm.exceptions import (
    AuthenticationError,
    ContextWindowExceededError,
    InvalidModelError,
    LLMProviderError,
    ProviderError,
    ProviderUnavailableError,
    RateLimitError,
)
from app.infrastructure.llm.factory import LLMProviderFactory
from app.infrastructure.llm.message import ChatMessage, MessageRole
from app.infrastructure.llm.models import ModelInfo
from app.infrastructure.llm.provider import LLMProvider
from app.infrastructure.llm.providers.ollama_provider import OllamaProvider
from app.infrastructure.llm.providers.openai_provider import OpenAIProvider
from app.infrastructure.llm.registry import (
    LLMProviderRegistry,
    get_default_registry,
)
from app.infrastructure.llm.response import (
    ChatRequest,
    ChatResponse,
    CompletionUsage,
    StreamChunk,
)
from app.infrastructure.llm.streaming import AsyncStreamWrapper

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
