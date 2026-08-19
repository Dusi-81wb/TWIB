"""OmniRoute LLM Gateway implementation.

Provides an OpenAI-compatible async gateway client connecting to any LLM proxy,
local server (e.g. LM Studio, Ollama), or OpenAI-compatible provider.
Reads configuration dynamically from ApplicationSettings and maps responses to TWIB-specific models.
"""

from __future__ import annotations

import json
import time
from collections.abc import Sequence
from typing import Any

import httpx
import structlog

from app.core.settings import ApplicationSettings
from app.infrastructure.llm.exceptions import (
    GatewayAuthError,
    GatewayTimeoutError,
    GatewayUnavailableError,
    ProviderError,
)
from app.infrastructure.llm.gateway import LLMGateway
from app.infrastructure.llm.message import ChatMessage, MessageRole
from app.infrastructure.llm.models import GatewayResponse, GatewayUsage

logger = structlog.get_logger(__name__)


def _detect_provider_name(base_url: str) -> str:
    """Return a human-friendly provider name based on endpoint URL."""
    lowered = base_url.lower()
    if "1234" in lowered or "lmstudio" in lowered:
        return "lm_studio"
    if "11434" in lowered or "ollama" in lowered:
        return "ollama"
    if "openrouter.ai" in lowered:
        return "openrouter"
    if "api.openai.com" in lowered:
        return "openai"
    if "groq.com" in lowered:
        return "groq"
    if "localhost:8080" in lowered or "omniroute" in lowered or "20128" in lowered:
        return "omniroute"
    return "openai_compatible"


class OmniRouteGateway(LLMGateway):
    """Provider-agnostic LLM Gateway implementation.

    Communicates with OpenAI-compatible ``/v1/chat/completions`` endpoints (OmniRoute,
    LM Studio, Ollama, OpenRouter, OpenAI, Groq, etc.), mapping responses to TWIB-specific
    ``GatewayResponse`` objects.
    """

    def __init__(
        self,
        settings: ApplicationSettings | None = None,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        default_model: str | None = None,
        http_client: httpx.AsyncClient | None = None,
        timeout: float = 60.0,
    ) -> None:
        """Initialize OmniRouteGateway with settings or explicit credentials.

        Args:
            settings: Optional ApplicationSettings instance to pull defaults dynamically from.
            base_url: Explicit base URL override for LLM Gateway API.
            api_key: Explicit API key override.
            default_model: Explicit default model identifier override.
            http_client: Optional injected httpx.AsyncClient instance.
            timeout: Default request timeout in seconds.
        """
        self._settings = settings
        self._explicit_base_url = base_url
        self._explicit_api_key = api_key
        self._explicit_default_model = default_model
        self._timeout = timeout
        self._external_client = http_client is not None
        self._client = http_client or httpx.AsyncClient(timeout=timeout)

    @property
    def base_url(self) -> str:
        """Return configured base URL, stripped of trailing slashes."""
        if self._explicit_base_url:
            return self._explicit_base_url.rstrip("/")
        if self._settings and self._settings.omniroute_base_url:
            return self._settings.omniroute_base_url.rstrip("/")
        return "http://localhost:8080/v1"

    @property
    def default_model(self) -> str:
        """Return configured default model identifier."""
        if self._explicit_default_model and self._explicit_default_model != "default":
            return self._explicit_default_model
        if self._settings and self._settings.default_model and self._settings.default_model != "default":
            return self._settings.default_model
        return "best-free"

    @property
    def api_key(self) -> str:
        """Return configured API key."""
        if self._explicit_api_key is not None:
            return self._explicit_api_key
        if self._settings and self._settings.omniroute_api_key:
            return self._settings.omniroute_api_key
        return ""

    @property
    def provider_name(self) -> str:
        """Return detected provider name string."""
        return _detect_provider_name(self.base_url)

    def _get_headers(self) -> dict[str, str]:
        """Construct request headers including authorization if API key is present."""
        headers = {"Content-Type": "application/json"}
        key = self.api_key.strip()
        if key:
            headers["Authorization"] = f"Bearer {key}"
        return headers

    def _get_completions_url(self) -> str:
        """Resolve full chat completions URL ensuring correct /v1 prefix with no duplicates."""
        base = self.base_url.rstrip("/")
        if base.endswith("/v1"):
            return f"{base}/chat/completions"
        return f"{base}/v1/chat/completions"

    def _get_models_url(self) -> str:
        """Resolve models discovery URL ensuring correct /v1 prefix with no duplicates."""
        base = self.base_url.rstrip("/")
        if base.endswith("/v1"):
            return f"{base}/models"
        return f"{base}/v1/models"

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
        """Resolve a valid model identifier dynamically from endpoint or settings."""
        # 1. If an explicit, non-generic model is requested, use it directly
        if requested_model and requested_model not in self.GENERIC_MODEL_IDENTIFIERS:
            return requested_model

        # 2. Check if a non-generic model is explicitly configured in settings
        configured = self.default_model
        if configured and configured not in self.GENERIC_MODEL_IDENTIFIERS:
            return configured

        # 3. If model is generic or missing, query available/loaded models from endpoint dynamically
        try:
            models_url = self._get_models_url()
            headers = self._get_headers()
            resp = await self._client.get(models_url, headers=headers, timeout=2.0)
            if resp.status_code == 200:
                data = resp.json()
                if "data" in data and isinstance(data["data"], list) and len(data["data"]) > 0:
                    loaded_models: list[str] = []
                    all_models: list[str] = []
                    for item in data["data"]:
                        mid = item.get("id")
                        if mid:
                            all_models.append(str(mid))
                            if item.get("loaded") is True or item.get("state") == "loaded":
                                loaded_models.append(str(mid))

                    chosen = loaded_models or all_models
                    if chosen:
                        return chosen[0]
        except Exception:
            pass

        # 4. Fallback if discovery failed or endpoint does not support /models
        if requested_model and requested_model != "default":
            return requested_model

        if configured and configured != "default":
            return configured

        return "best-free"

    async def chat(
        self,
        messages: Sequence[ChatMessage | dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float | None = None,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> GatewayResponse:
        """Send a sequence of messages to OpenAI-compatible chat completions endpoint.

        Args:
            messages: Conversation messages (ChatMessage objects or dicts).
            model: Optional override model identifier.
            temperature: Optional sampling temperature override.
            system_prompt: Optional prepended system message.
            **kwargs: Extra parameters passed to the request payload.

        Returns:
            TWIB-specific GatewayResponse object.

        Raises:
            GatewayTimeoutError: When gateway request times out.
            GatewayAuthError: When gateway returns 401/403.
            GatewayUnavailableError: When gateway server is unreachable or 502/503/504.
            ProviderError: For general request errors.
        """
        target_model = await self._resolve_target_model(model)
        formatted_messages: list[dict[str, Any]] = []

        if system_prompt:
            formatted_messages.append(
                {"role": MessageRole.SYSTEM.value, "content": system_prompt}
            )

        for msg in messages:
            if isinstance(msg, ChatMessage):
                role_val = (
                    msg.role.value if hasattr(msg.role, "value") else str(msg.role)
                )
                formatted_messages.append({"role": role_val, "content": msg.content})
            elif isinstance(msg, dict):
                role_str = str(msg.get("role", "user"))
                content_str = str(msg.get("content", ""))
                formatted_messages.append({"role": role_str, "content": content_str})

        payload: dict[str, Any] = {
            "model": target_model,
            "messages": formatted_messages,
            "stream": False,
        }
        if temperature is not None:
            payload["temperature"] = temperature
        payload.update(kwargs)

        url = self._get_completions_url()
        headers = self._get_headers()
        provider_name = self.provider_name

        log = logger.bind(
            provider=provider_name,
            model=target_model,
            url=url,
            message_count=len(formatted_messages),
        )
        log.debug("Sending chat completion request to LLM Gateway", url=url)

        start_time = time.perf_counter()
        try:
            response = await self._client.post(
                url,
                json=payload,
                headers=headers,
                timeout=self._timeout,
            )
            response.raise_for_status()
        except httpx.TimeoutException as err:
            log.warning("LLM Gateway request timed out", timeout=self._timeout, endpoint=url)
            raise GatewayTimeoutError(
                f"LLM Gateway ({provider_name}) timed out after {self._timeout}s reaching {url} for model '{target_model}'",
                provider=provider_name,
                model=target_model,
            ) from err
        except httpx.HTTPStatusError as err:
            status_code = err.response.status_code
            resp_snippet = err.response.text[:200]
            log.error(
                "LLM Gateway returned HTTP error status",
                status_code=status_code,
                endpoint=url,
                response_text=resp_snippet,
            )
            if status_code in (401, 403):
                raise GatewayAuthError(
                    f"Authentication failed for {provider_name} at {url} (HTTP {status_code}). Check your configured API key.",
                    provider=provider_name,
                    model=target_model,
                    status_code=status_code,
                ) from err
            if status_code in (502, 503, 504):
                raise GatewayUnavailableError(
                    f"{provider_name} gateway server unavailable at {url} (HTTP {status_code}): {resp_snippet}",
                    provider=provider_name,
                    model=target_model,
                    status_code=status_code,
                ) from err
            raise ProviderError(
                f"{provider_name} request failed at {url} (HTTP {status_code}): {resp_snippet}",
                provider=provider_name,
                model=target_model,
                status_code=status_code,
            ) from err
        except httpx.RequestError as err:
            log.error("Failed to connect to LLM gateway endpoint", endpoint=url, error=str(err))
            raise GatewayUnavailableError(
                f"Could not connect to {provider_name} at {url}: {err}. Ensure the endpoint is running and reachable.",
                provider=provider_name,
                model=target_model,
            ) from err

        latency_ms = (time.perf_counter() - start_time) * 1000.0
        raw_text = response.text.strip()
        content_type = response.headers.get("content-type", "")

        answer = ""
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0
        returned_model = target_model

        if "text/event-stream" in content_type or raw_text.startswith("data:"):
            chunks: list[str] = []
            for line in raw_text.splitlines():
                clean_line = line.strip()
                if clean_line.startswith("data: ") and clean_line != "data: [DONE]":
                    try:
                        chunk_data = json.loads(clean_line[6:])
                        choices = chunk_data.get("choices", [])
                        if choices and isinstance(choices, list):
                            delta = choices[0].get("delta", {})
                            if isinstance(delta, dict) and "content" in delta:
                                chunks.append(str(delta["content"]))
                        if "usage" in chunk_data and isinstance(
                            chunk_data["usage"], dict
                        ):
                            u = chunk_data["usage"]
                            prompt_tokens = u.get("prompt_tokens", prompt_tokens)
                            completion_tokens = u.get(
                                "completion_tokens", completion_tokens
                            )
                            total_tokens = u.get("total_tokens", total_tokens)
                        if chunk_data.get("model"):
                            returned_model = str(chunk_data["model"])
                    except Exception as parse_err:
                        log.debug("Skipping unparseable SSE line", error=str(parse_err))
            answer = "".join(chunks)
        else:
            try:
                data = response.json()
            except Exception as err:
                log.error(
                    "Failed to decode JSON response from LLM Gateway",
                    text=raw_text[:200],
                )
                raise ProviderError(
                    f"{provider_name} returned non-JSON response from {url}: {err}",
                    provider=provider_name,
                    model=target_model,
                ) from err

            choices = data.get("choices", [])
            if choices and isinstance(choices, list) and len(choices) > 0:
                first_choice = choices[0]
                if isinstance(first_choice, dict) and "message" in first_choice:
                    msg = first_choice["message"]
                    if isinstance(msg, dict):
                        # Support content and reasoning_content
                        content_val = msg.get("content")
                        if content_val:
                            answer = str(content_val).strip()
                        elif msg.get("reasoning_content"):
                            answer = str(msg.get("reasoning_content")).strip()

            raw_usage = data.get("usage", {})
            if isinstance(raw_usage, dict):
                prompt_tokens = raw_usage.get("prompt_tokens", 0)
                completion_tokens = raw_usage.get("completion_tokens", 0)
                total_tokens = raw_usage.get("total_tokens", 0)

            returned_model = str(data.get("model") or target_model)

        usage = GatewayUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens or (prompt_tokens + completion_tokens),
        )

        return GatewayResponse(
            answer=answer,
            model=returned_model,
            provider=provider_name,
            usage=usage,
            latency_ms=round(latency_ms, 2),
            raw_response=response.json() if not raw_text.startswith("data:") else None,
        )

    async def complete(
        self,
        prompt: str,
        *,
        model: str | None = None,
        temperature: float | None = None,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> GatewayResponse:
        """Send a single prompt string for completion."""
        user_msg = ChatMessage(role=MessageRole.USER, content=prompt)
        return await self.chat(
            [user_msg],
            model=model,
            temperature=temperature,
            system_prompt=system_prompt,
            **kwargs,
        )

    async def generate(
        self,
        prompt: str,
        *,
        model: str | None = None,
        temperature: float | None = None,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> GatewayResponse:
        """Alias for complete() method."""
        return await self.complete(
            prompt=prompt,
            model=model,
            temperature=temperature,
            system_prompt=system_prompt,
            **kwargs,
        )

    async def health(self) -> dict[str, Any]:
        """Check operational health and reachability of the LLM gateway endpoint.

        Returns:
            Dictionary containing health status, latency_ms, base_url, and model count.
        """
        start_time = time.perf_counter()
        headers = self._get_headers()
        health_url = self._get_models_url()
        provider_name = self.provider_name

        try:
            response = await self._client.get(health_url, headers=headers, timeout=5.0)
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            is_healthy = response.status_code < 500
            model_count = 0
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "data" in data and isinstance(data["data"], list):
                        model_count = len(data["data"])
                except Exception:
                    pass

            return {
                "status": "healthy" if is_healthy else "unhealthy",
                "provider": provider_name,
                "base_url": self.base_url,
                "status_code": response.status_code,
                "latency_ms": round(latency_ms, 2),
                "model_count": model_count,
            }
        except Exception as err:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            logger.warning("LLM Gateway health check failed", endpoint=health_url, error=str(err))
            return {
                "status": "unhealthy",
                "provider": provider_name,
                "base_url": self.base_url,
                "latency_ms": round(latency_ms, 2),
                "error": str(err),
            }

    async def close(self) -> None:
        """Close the underlying HTTP client if created internally."""
        if not self._external_client:
            await self._client.aclose()
