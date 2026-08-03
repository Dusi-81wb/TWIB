"""OpenAI LLM provider implementation.

Implements the :class:`~app.infrastructure.llm.provider.LLMProvider` contract
backed by the official ``openai.AsyncOpenAI`` client SDK. Converts all
OpenAI-specific exceptions into shared TWIB provider exceptions.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

try:
    import openai
    from openai import AsyncOpenAI
except ImportError:  # pragma: no cover
    openai = None  # type: ignore[assignment]
    AsyncOpenAI = None  # type: ignore[assignment, misc]

from app.core.config import get_settings
from app.core.settings import ApplicationSettings
from app.infrastructure.llm.exceptions import (
    AuthenticationError,
    ContextWindowExceededError,
    InvalidModelError,
    LLMProviderError,
    ProviderError,
    ProviderUnavailableError,
    RateLimitError,
)
from app.infrastructure.llm.message import ChatMessage, MessageRole
from app.infrastructure.llm.models import ModelInfo
from app.infrastructure.llm.provider import LLMProvider
from app.infrastructure.llm.response import (
    ChatRequest,
    ChatResponse,
    CompletionUsage,
    StreamChunk,
)

DEFAULT_OPENAI_MODELS = [
    ModelInfo(
        id="gpt-4o",
        name="GPT-4o",
        provider="openai",
        context_window=128000,
        max_output_tokens=4096,
        supports_streaming=True,
        supports_tools=True,
        supports_vision=True,
    ),
    ModelInfo(
        id="gpt-4o-mini",
        name="GPT-4o Mini",
        provider="openai",
        context_window=128000,
        max_output_tokens=4096,
        supports_streaming=True,
        supports_tools=True,
        supports_vision=True,
    ),
    ModelInfo(
        id="gpt-4-turbo",
        name="GPT-4 Turbo",
        provider="openai",
        context_window=128000,
        max_output_tokens=4096,
        supports_streaming=True,
        supports_tools=True,
        supports_vision=True,
    ),
    ModelInfo(
        id="gpt-3.5-turbo",
        name="GPT-3.5 Turbo",
        provider="openai",
        context_window=16385,
        max_output_tokens=4096,
        supports_streaming=True,
        supports_tools=True,
        supports_vision=False,
    ),
]


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider implementation.

    Attributes:
        provider_name: Always 'openai'.
        _client: AsyncOpenAI client instance.
    """

    provider_name: str = "openai"

    def __init__(
        self,
        api_key: str | None = None,
        client: Any | None = None,
        settings: ApplicationSettings | None = None,
    ) -> None:
        """Initialize OpenAIProvider.

        Args:
            api_key: Optional explicit OpenAI API key.
            client: Optional pre-configured AsyncOpenAI client instance.
            settings: Optional ApplicationSettings instance.
        """
        app_settings = settings or get_settings()
        key = api_key or app_settings.openai_api_key

        if client is not None:
            self._client = client
        elif AsyncOpenAI is not None and key:
            self._client = AsyncOpenAI(api_key=key)
        else:
            self._client = None

    async def complete(self, request: ChatRequest) -> ChatResponse:
        """Execute a non-streaming chat completion with OpenAI.

        Args:
            request: Provider-independent ChatRequest.

        Returns:
            Provider-independent ChatResponse.

        Raises:
            AuthenticationError: If API key is missing/invalid.
            RateLimitError: If rate limit is exceeded.
            InvalidModelError: If model is not found.
            LLMProviderError: On other completion failures.
        """
        client = self._get_client_or_raise()
        messages = self._format_messages(request.messages)

        kwargs: dict[str, Any] = {
            "model": request.model,
            "messages": messages,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "stream": False,
        }
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens
        if request.stop is not None:
            kwargs["stop"] = request.stop

        try:
            res = await client.chat.completions.create(**kwargs)
            choice = res.choices[0]
            message = ChatMessage(
                role=choice.message.role or MessageRole.ASSISTANT,
                content=choice.message.content or "",
            )
            usage = CompletionUsage(
                prompt_tokens=res.usage.prompt_tokens if res.usage else 0,
                completion_tokens=res.usage.completion_tokens if res.usage else 0,
                total_tokens=res.usage.total_tokens if res.usage else 0,
            )

            return ChatResponse(
                id=res.id,
                model=res.model,
                provider=self.provider_name,
                message=message,
                finish_reason=choice.finish_reason or "stop",
                usage=usage,
            )
        except Exception as err:
            raise self._map_exception(err, request.model) from err

    async def stream(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        """Execute a streaming chat completion with OpenAI.

        Args:
            request: Provider-independent ChatRequest.

        Yields:
            StreamChunk instances as tokens arrive.

        Raises:
            LLMProviderError: On streaming failure.
        """
        client = self._get_client_or_raise()
        messages = self._format_messages(request.messages)

        kwargs: dict[str, Any] = {
            "model": request.model,
            "messages": messages,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "stream": True,
        }
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens
        if request.stop is not None:
            kwargs["stop"] = request.stop

        try:
            response_stream = await client.chat.completions.create(**kwargs)
            async for chunk in response_stream:
                if not chunk.choices:
                    continue
                choice = chunk.choices[0]
                delta_text = choice.delta.content or ""
                yield StreamChunk(
                    id=chunk.id,
                    model=chunk.model,
                    provider=self.provider_name,
                    delta=delta_text,
                    finish_reason=choice.finish_reason,
                )
        except Exception as err:
            raise self._map_exception(err, request.model) from err

    async def list_models(self) -> list[ModelInfo]:
        """List models available from OpenAI.

        Returns:
            List of ModelInfo objects.

        Raises:
            LLMProviderError: On listing failure.
        """
        if self._client is None:
            return DEFAULT_OPENAI_MODELS

        try:
            models_page = await self._client.models.list()
            fetched_ids = {m.id for m in models_page.data}
            result: list[ModelInfo] = []
            for default_m in DEFAULT_OPENAI_MODELS:
                if default_m.id in fetched_ids:
                    result.append(default_m)
            # Add any additional OpenAI models returned by API
            for m in models_page.data:
                if m.id.startswith(("gpt-3.5", "gpt-4", "o1", "o3")) and not any(
                    r.id == m.id for r in result
                ):
                    result.append(
                        ModelInfo(
                            id=m.id,
                            name=m.id.upper(),
                            provider=self.provider_name,
                            context_window=4096,
                        )
                    )
            return result or DEFAULT_OPENAI_MODELS
        except Exception as err:
            # Fall back to default model list if listing fails
            _ = err
            return DEFAULT_OPENAI_MODELS

    async def health_check(self) -> bool:
        """Check whether OpenAI API is reachable and authentication succeeds.

        Returns:
            True if healthy, False otherwise.
        """
        if self._client is None:
            return False
        try:
            await self._client.models.list()
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    def _get_client_or_raise(self) -> Any:
        """Return configured AsyncOpenAI client or raise AuthenticationError.

        Returns:
            The active AsyncOpenAI client instance.

        Raises:
            AuthenticationError: If API key is missing or client is uninitialized.
        """
        if self._client is None:
            raise AuthenticationError(
                "OpenAI API key is missing or client is uninitialized",
                provider=self.provider_name,
            )
        return self._client

    @staticmethod
    def _format_messages(messages: list[ChatMessage]) -> list[dict[str, Any]]:
        """Format list of ChatMessage into OpenAI API format.

        Args:
            messages: List of ChatMessage objects.

        Returns:
            List of message dicts matching OpenAI SDK format.
        """
        result: list[dict[str, Any]] = []
        for msg in messages:
            role = msg.role.value if hasattr(msg.role, "value") else str(msg.role)
            item: dict[str, Any] = {
                "role": role,
                "content": msg.content,
            }
            if msg.name:
                item["name"] = msg.name
            result.append(item)
        return result

    def _map_exception(self, err: Exception, model: str) -> LLMProviderError:
        """Map an OpenAI SDK exception or generic exception to shared LLMProviderError.

        Args:
            err: The caught exception.
            model: The target model name.

        Returns:
            An LLMProviderError subclass instance.
        """
        msg = str(err)
        if openai is not None:
            p_name = self.provider_name
            if isinstance(err, openai.AuthenticationError):
                return AuthenticationError(msg, provider=p_name, model=model)
            if isinstance(err, openai.RateLimitError):
                return RateLimitError(msg, provider=p_name, model=model)
            if isinstance(err, openai.NotFoundError):
                return InvalidModelError(msg, provider=p_name, model=model)
            if isinstance(err, (openai.APIConnectionError, openai.APITimeoutError)):
                return ProviderUnavailableError(
                    msg, provider=self.provider_name, model=model
                )
            if isinstance(err, openai.BadRequestError):
                if "context_length" in msg.lower() or "maximum context" in msg.lower():
                    return ContextWindowExceededError(
                        msg, provider=self.provider_name, model=model
                    )
                return ProviderError(msg, provider=self.provider_name, model=model)
            if isinstance(err, openai.OpenAIError):
                return ProviderError(msg, provider=self.provider_name, model=model)

        return ProviderError(msg, provider=self.provider_name, model=model)
