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
        self._settings = settings
        self._explicit_key = api_key
        self._explicit_client = client

    @property
    def _app_settings(self) -> ApplicationSettings:
        return self._settings or get_settings()

    @property
    def _client(self) -> Any:
        try:
            return self._get_client_or_raise()
        except Exception:
            return None

    def _get_client_or_raise(self) -> Any:
        """Return configured AsyncOpenAI client or dynamically build from current settings."""
        if self._explicit_client is not None:
            return self._explicit_client

        if AsyncOpenAI is None:
            raise AuthenticationError(
                "AsyncOpenAI SDK is not available.",
                provider=self.provider_name,
            )

        app_settings = self._app_settings
        key = self._explicit_key or app_settings.omniroute_api_key or app_settings.openai_api_key or "sk-omniroute"
        base_url = (
            app_settings.omniroute_base_url
            if app_settings.omniroute_base_url
            else (app_settings.openai_api_base if app_settings.openai_api_key else "http://localhost:8080/v1")
        )

        clean_url = (base_url or "http://localhost:8080/v1").rstrip("/")
        if not clean_url.endswith("/v1"):
            clean_url = f"{clean_url}/v1"

        client_kwargs: dict[str, Any] = {
            "api_key": key,
            "base_url": clean_url,
        }
        return AsyncOpenAI(**client_kwargs)

    GENERIC_MODEL_IDENTIFIERS = {
        "default",
        "best-fast",
        "best-free",
        "best",
        "auto",
        "fast",
        "free",
        "omniroute/auto",
        "custom",
    }

    async def _resolve_target_model(self, requested_model: str | None) -> str:
        """Resolve valid model identifier dynamically from endpoint or settings."""
        app_settings = self._app_settings
        configured = app_settings.default_model

        # 1. If an explicit non-generic model is requested, use it
        if requested_model and requested_model not in self.GENERIC_MODEL_IDENTIFIERS:
            if requested_model != "gpt-4o" or (configured == "gpt-4o" or "openai.com" in (app_settings.omniroute_base_url or "")):
                return requested_model

        # 2. Check if a non-generic model is explicitly configured in settings
        if configured and configured not in self.GENERIC_MODEL_IDENTIFIERS and configured != "gpt-4o":
            return configured

        # 3. Query loaded models from endpoint dynamically if available
        try:
            discovered = await self.list_models()
            model_ids = [m.id for m in discovered if m.id and m.id not in self.GENERIC_MODEL_IDENTIFIERS]
            if model_ids:
                return model_ids[0]
        except Exception:
            pass

        # 4. Fallback if listing was unavailable
        if requested_model and requested_model != "default":
            return requested_model

        if configured and configured != "default":
            return configured

        return "best-free"

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
        target_model = await self._resolve_target_model(request.model)

        kwargs: dict[str, Any] = {
            "model": target_model,
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
            raise self._map_exception(err, target_model) from err

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
        target_model = await self._resolve_target_model(request.model)

        kwargs: dict[str, Any] = {
            "model": target_model,
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
            raise self._map_exception(err, target_model) from err

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
            result: list[ModelInfo] = []
            for m in models_page.data:
                mid = getattr(m, "id", None) or (m.get("id") if isinstance(m, dict) else str(m))
                if mid:
                    result.append(
                        ModelInfo(
                            id=mid,
                            name=mid,
                            provider=self.provider_name,
                            context_window=8192,
                        )
                    )
            return result or DEFAULT_OPENAI_MODELS
        except Exception as err:
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
