"""LLM Provider and Gateway abstraction package.

Exposes provider-independent interfaces, gateways, models, exceptions, and types:

- :class:`.LLMGateway`: Abstract base class for LLM gateways.
- :class:`.OmniRouteGateway`: OmniRoute gateway client implementation.
- :class:`.GatewayResponse`: TWIB-specific gateway response model.
- :class:`.GatewayUsage`: Token usage metrics for gateway responses.
- :class:`.LLMProvider`: Abstract base class for LLM providers.
- :class:`.ChatMessage`: Unified chat message representation.
- :class:`.MessageRole`: Conversation author role enumeration.
- :class:`.ChatRequest`: Completion request payload.
- :class:`.ChatResponse`: Completion response object.
- :class:`.StreamChunk`: Streaming content delta chunk.
- :class:`.CompletionUsage`: Token usage metrics.
- :class:`.ModelInfo`: Model metadata and capabilities.
- :class:`.LLMProviderError`: Base exception for LLM provider errors.
- :class:`.GatewayError`: Base exception for gateway errors.
"""

from app.infrastructure.llm.conversation import Conversation
from app.infrastructure.llm.exceptions import (
    AuthenticationError,
    ContextWindowExceededError,
    GatewayAuthError,
    GatewayError,
    GatewayTimeoutError,
    GatewayUnavailableError,
    InvalidModelError,
    LLMProviderError,
    ProviderError,
    ProviderUnavailableError,
    RateLimitError,
)
from app.infrastructure.llm.factory import LLMProviderFactory
from app.infrastructure.llm.gateway import LLMGateway
from app.infrastructure.llm.message import ChatMessage, MessageRole
from app.infrastructure.llm.models import GatewayResponse, GatewayUsage, ModelInfo
from app.infrastructure.llm.omniroute_gateway import OmniRouteGateway
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
    "GatewayAuthError",
    "GatewayError",
    "GatewayResponse",
    "GatewayTimeoutError",
    "GatewayUnavailableError",
    "GatewayUsage",
    "InvalidModelError",
    "LLMGateway",
    "LLMProvider",
    "LLMProviderError",
    "LLMProviderFactory",
    "LLMProviderRegistry",
    "MessageRole",
    "ModelInfo",
    "OllamaProvider",
    "OmniRouteGateway",
    "OpenAIProvider",
    "ProviderError",
    "ProviderUnavailableError",
    "RateLimitError",
    "StreamChunk",
    "get_default_registry",
]
