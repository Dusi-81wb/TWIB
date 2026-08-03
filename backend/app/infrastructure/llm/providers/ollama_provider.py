"""Ollama local LLM provider implementation.

Implements the :class:`~app.infrastructure.llm.provider.LLMProvider` contract
backed by the local Ollama REST API over async HTTP (httpx). Converts all HTTP
and network exceptions into shared TWIB LLM provider exceptions.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator
from typing import Any

import httpx

from app.core.config import get_settings
from app.core.settings import ApplicationSettings
from app.infrastructure.llm.exceptions import (
    ContextWindowExceededError,
    InvalidModelError,
    LLMProviderError,
    ProviderError,
    ProviderUnavailableError,
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

DEFAULT_OLLAMA_MODELS = [
    ModelInfo(
        id="llama3",
        name="Llama 3",
        provider="ollama",
        context_window=8192,
        supports_streaming=True,
        supports_tools=False,
        supports_vision=False,
    ),
    ModelInfo(
        id="mistral",
        name="Mistral 7B",
        provider="ollama",
        context_window=8192,
        supports_streaming=True,
        supports_tools=False,
        supports_vision=False,
    ),
    ModelInfo(
        id="codellama",
        name="Code Llama",
        provider="ollama",
        context_window=16384,
        supports_streaming=True,
        supports_tools=False,
        supports_vision=False,
    ),
]


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider implementation.

    Attributes:
        provider_name: Always 'ollama'.
        _base_url: Base URL of the Ollama server (e.g. 'http://localhost:11434').
    """

    provider_name: str = "ollama"

    def __init__(
        self,
        base_url: str | None = None,
        client: httpx.AsyncClient | None = None,
        settings: ApplicationSettings | None = None,
    ) -> None:
        """Initialize OllamaProvider.

        Args:
            base_url: Optional explicit base URL string.
            client: Optional pre-configured httpx.AsyncClient.
            settings: Optional ApplicationSettings instance.
        """
        app_settings = settings or get_settings()
        url = base_url or app_settings.ollama_base_url or "http://localhost:11434"
        self._base_url = url.rstrip("/")
        self._client = client

    async def complete(self, request: ChatRequest) -> ChatResponse:
        """Execute a non-streaming chat completion with local Ollama server.

        Args:
            request: Provider-independent ChatRequest.

        Returns:
            Provider-independent ChatResponse.

        Raises:
            InvalidModelError: If model is unknown or not pulled.
            ProviderUnavailableError: If Ollama server is unreachable.
            LLMProviderError: On other completion failures.
        """
        endpoint = f"{self._base_url}/api/chat"
        payload = self._build_payload(request, stream=False)

        try:
            async with self._get_client() as client:
                res = await client.post(endpoint, json=payload, timeout=120.0)
                self._check_status(res, request.model)
                data = res.json()

            msg_data = data.get("message", {})
            message = ChatMessage(
                role=msg_data.get("role", MessageRole.ASSISTANT),
                content=msg_data.get("content", ""),
            )
            p_count = data.get("prompt_eval_count", 0)
            e_count = data.get("eval_count", 0)
            usage = CompletionUsage(
                prompt_tokens=p_count,
                completion_tokens=e_count,
                total_tokens=p_count + e_count,
            )

            return ChatResponse(
                id=str(uuid.uuid4()),
                model=data.get("model", request.model),
                provider=self.provider_name,
                message=message,
                finish_reason=data.get("done_reason", "stop"),
                usage=usage,
            )
        except Exception as err:
            raise self._map_exception(err, request.model) from err

    async def stream(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        """Execute a streaming chat completion with local Ollama server.

        Args:
            request: Provider-independent ChatRequest.

        Yields:
            StreamChunk instances as content arrives.

        Raises:
            LLMProviderError: On streaming failure.
        """
        endpoint = f"{self._base_url}/api/chat"
        payload = self._build_payload(request, stream=True)
        chunk_id = str(uuid.uuid4())

        try:
            client = httpx.AsyncClient(timeout=120.0)
            async with client.stream("POST", endpoint, json=payload) as response:
                self._check_status(response, request.model)
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    msg_data = data.get("message", {})
                    delta_text = msg_data.get("content", "")
                    done = data.get("done", False)
                    finish_reason = data.get("done_reason", "stop") if done else None

                    usage: CompletionUsage | None = None
                    if done and ("eval_count" in data or "prompt_eval_count" in data):
                        p_tokens = data.get("prompt_eval_count", 0)
                        c_tokens = data.get("eval_count", 0)
                        usage = CompletionUsage(
                            prompt_tokens=p_tokens,
                            completion_tokens=c_tokens,
                            total_tokens=p_tokens + c_tokens,
                        )

                    yield StreamChunk(
                        id=chunk_id,
                        model=data.get("model", request.model),
                        provider=self.provider_name,
                        delta=delta_text,
                        finish_reason=finish_reason,
                        usage=usage,
                    )
        except Exception as err:
            raise self._map_exception(err, request.model) from err

    async def list_models(self) -> list[ModelInfo]:
        """List local models available in Ollama server (`GET /api/tags`).

        Returns:
            List of ModelInfo objects.

        Raises:
            LLMProviderError: On listing failure.
        """
        endpoint = f"{self._base_url}/api/tags"
        try:
            async with self._get_client() as client:
                res = await client.get(endpoint, timeout=10.0)
                if res.status_code != 200:
                    return DEFAULT_OLLAMA_MODELS
                data = res.json()

            models_data = data.get("models", [])
            if not models_data:
                return DEFAULT_OLLAMA_MODELS

            result: list[ModelInfo] = []
            for m in models_data:
                model_name = m.get("name", "unknown")
                details = m.get("details", {})
                result.append(
                    ModelInfo(
                        id=model_name,
                        name=model_name,
                        provider=self.provider_name,
                        context_window=8192,
                        metadata=details,
                    )
                )
            return result
        except Exception:
            return DEFAULT_OLLAMA_MODELS

    async def health_check(self) -> bool:
        """Check whether local Ollama server is running and reachable.

        Returns:
            True if healthy, False otherwise.
        """
        endpoint = f"{self._base_url}/api/version"
        try:
            async with self._get_client() as client:
                res = await client.get(endpoint, timeout=5.0)
                return res.status_code == 200
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    def _get_client(self) -> httpx.AsyncClient:
        """Return configured httpx.AsyncClient or new context instance."""
        if self._client is not None:
            return self._client
        return httpx.AsyncClient(timeout=30.0)

    @staticmethod
    def _build_payload(request: ChatRequest, stream: bool) -> dict[str, Any]:
        """Build Ollama /api/chat JSON payload from ChatRequest.

        Args:
            request: ChatRequest object.
            stream: Boolean stream flag.

        Returns:
            Dict payload matching Ollama REST API.
        """
        messages = [
            {
                "role": (m.role.value if hasattr(m.role, "value") else str(m.role)),
                "content": m.content,
            }
            for m in request.messages
        ]

        options: dict[str, Any] = {
            "temperature": request.temperature,
            "top_p": request.top_p,
        }
        if request.max_tokens is not None:
            options["num_predict"] = request.max_tokens
        if request.stop is not None:
            options["stop"] = request.stop

        return {
            "model": request.model,
            "messages": messages,
            "stream": stream,
            "options": options,
        }

    @staticmethod
    def _check_status(res: httpx.Response, model: str) -> None:
        """Check HTTP response status code and raise appropriate domain exception.

        Args:
            res: HTTP status response.
            model: Target model string.

        Raises:
            InvalidModelError: 404 response.
            ContextWindowExceededError: 400 response.
            ProviderError: Non-200 status response.
        """
        if res.status_code == 200:
            return
        if res.status_code == 404:
            raise InvalidModelError(
                f"Ollama model '{model}' not found or not pulled",
                provider="ollama",
                model=model,
            )
        if res.status_code == 400:
            raise ContextWindowExceededError(
                f"Ollama bad request: {res.text}",
                provider="ollama",
                model=model,
            )
        raise ProviderError(
            f"Ollama server returned status {res.status_code}: {res.text}",
            provider="ollama",
            model=model,
        )

    def _map_exception(self, err: Exception, model: str) -> LLMProviderError:
        """Map caught exceptions to LLMProviderError subclasses.

        Args:
            err: Caught exception instance.
            model: Target model string.

        Returns:
            LLMProviderError subclass instance.
        """
        if isinstance(err, LLMProviderError):
            return err

        msg = str(err)
        network_errors = (
            httpx.ConnectError,
            httpx.TimeoutException,
            httpx.NetworkError,
        )
        if isinstance(err, network_errors):
            return ProviderUnavailableError(
                f"Ollama server at '{self._base_url}' is unreachable: {msg}",
                provider=self.provider_name,
                model=model,
            )

        return ProviderError(msg, provider=self.provider_name, model=model)
