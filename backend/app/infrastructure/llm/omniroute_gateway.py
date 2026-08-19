"""OmniRoute LLM Gateway implementation.

Provides an OpenAI-compatible async gateway client connecting to an OmniRoute LLM proxy.
Reads configuration from ApplicationSettings and maps responses to TWIB-specific models.
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


class OmniRouteGateway(LLMGateway):
    """Provider-agnostic LLM Gateway implementation backed by OmniRoute.

    Communicates with OpenAI-compatible ``/v1/chat/completions`` endpoints,
    mapping responses to TWIB-specific ``GatewayResponse`` objects.
    """

    def __init__(
        self,
        settings: ApplicationSettings | None = None,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        default_model: str | None = None,
        http_client: httpx.AsyncClient | None = None,
        timeout: float = 30.0,
    ) -> None:
        """Initialize OmniRouteGateway with settings or explicit credentials.

        Args:
            settings: Optional ApplicationSettings instance to pull defaults from.
            base_url: Explicit base URL override for OmniRoute API.
            api_key: Explicit API key override.
            default_model: Explicit default model identifier override.
            http_client: Optional injected httpx.AsyncClient instance.
            timeout: Default request timeout in seconds.
        """
        raw_url = base_url or (
            settings.omniroute_base_url if settings else "http://localhost:20128/v1"
        )
        self._base_url = raw_url.rstrip("/")
        self._api_key = (
            api_key
            if api_key is not None
            else (settings.omniroute_api_key if settings else "")
        )
        self._default_model = default_model or (
            settings.default_model if settings else "best-fast"
        )
        self._timeout = timeout
        self._external_client = http_client is not None
        self._client = http_client or httpx.AsyncClient(timeout=timeout)

    @property
    def base_url(self) -> str:
        """Return configured base URL for OmniRoute API."""
        return self._base_url

    @property
    def default_model(self) -> str:
        """Return configured default model identifier."""
        return self._default_model

    def _get_headers(self) -> dict[str, str]:
        """Construct request headers including authorization if API key is present."""
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    def _get_completions_url(self) -> str:
        """Resolve full completions URL handling base URL path structures."""
        if self._base_url.endswith("/v1"):
            return f"{self._base_url}/chat/completions"
        return f"{self._base_url}/v1/chat/completions"

    async def chat(
        self,
        messages: Sequence[ChatMessage | dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float | None = None,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> GatewayResponse:
        """Send a sequence of messages to OmniRoute chat completions endpoint.

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
        target_model = model or self._default_model
        if target_model and "/" not in target_model:
            target_model = f"auto/{target_model}"
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

        log = logger.bind(
            provider="omniroute",
            model=target_model,
            message_count=len(formatted_messages),
        )
        log.debug("Sending chat completion request to OmniRoute gateway", url=url)

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
            log.warning("OmniRoute gateway request timed out", timeout=self._timeout)
            raise GatewayTimeoutError(
                f"OmniRoute gateway request timed out after {self._timeout}s",
                provider="omniroute",
                model=target_model,
            ) from err
        except httpx.HTTPStatusError as err:
            status_code = err.response.status_code
            log.error(
                "OmniRoute gateway returned HTTP error status", status_code=status_code
            )
            if status_code in (401, 403):
                raise GatewayAuthError(
                    f"Authentication failed for OmniRoute gateway (HTTP {status_code})",
                    provider="omniroute",
                    model=target_model,
                    status_code=status_code,
                ) from err
            if status_code in (502, 503, 504):
                raise GatewayUnavailableError(
                    f"OmniRoute gateway server unavailable (HTTP {status_code})",
                    provider="omniroute",
                    model=target_model,
                    status_code=status_code,
                ) from err
            raise ProviderError(
                f"OmniRoute gateway request failed with HTTP {status_code}: "
                f"{err.response.text}",
                provider="omniroute",
                model=target_model,
                status_code=status_code,
            ) from err
        except httpx.RequestError as err:
            log.error("Failed to connect to OmniRoute gateway endpoint", error=str(err))
            raise GatewayUnavailableError(
                f"Could not connect to OmniRoute gateway endpoint: {err}",
                provider="omniroute",
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
                    "Failed to decode JSON response from OmniRoute",
                    text=raw_text[:200],
                )
                raise ProviderError(
                    f"OmniRoute gateway returned invalid response payload: {err}",
                    provider="omniroute",
                    model=target_model,
                ) from err

            choices = data.get("choices", [])
            if choices and isinstance(choices, list):
                first_choice = choices[0]
                if isinstance(first_choice, dict) and "message" in first_choice:
                    msg = first_choice["message"]
                    if isinstance(msg, dict):
                        answer = str(msg.get("content", ""))

            raw_usage = data.get("usage", {})
            if isinstance(raw_usage, dict):
                prompt_tokens = raw_usage.get("prompt_tokens", 0)
                completion_tokens = raw_usage.get("completion_tokens", 0)
                total_tokens = raw_usage.get("total_tokens", 0)

            returned_model = str(data.get("model") or target_model)

        usage = GatewayUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )

        log.info(
            "OmniRoute completion succeeded",
            latency_ms=round(latency_ms, 2),
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
        )

        return GatewayResponse(
            answer=answer,
            provider="omniroute",
            model=returned_model,
            latency_ms=round(latency_ms, 2),
            usage=usage,
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
        """Send a single prompt string for text completion.

        Args:
            prompt: Input prompt string.
            model: Optional override model identifier.
            temperature: Optional sampling temperature override.
            system_prompt: Optional system instructions.
            **kwargs: Extra parameters passed to chat completion call.

        Returns:
            TWIB-specific GatewayResponse object.
        """
        user_msg = ChatMessage(role=MessageRole.USER, content=prompt)
        return await self.chat(
            [user_msg],
            model=model,
            temperature=temperature,
            system_prompt=system_prompt,
            **kwargs,
        )

    async def health(self) -> dict[str, Any]:
        """Check operational health and reachability of OmniRoute gateway endpoint.

        Returns:
            Dictionary containing health status, latency_ms, and gateway metadata.
        """
        start_time = time.perf_counter()
        headers = self._get_headers()
        health_url = (
            f"{self._base_url}/models"
            if self._base_url.endswith("/v1")
            else f"{self._base_url}/v1/models"
        )

        try:
            response = await self._client.get(health_url, headers=headers, timeout=5.0)
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            is_healthy = response.status_code < 500
            return {
                "status": "healthy" if is_healthy else "unhealthy",
                "provider": "omniroute",
                "base_url": self._base_url,
                "status_code": response.status_code,
                "latency_ms": round(latency_ms, 2),
            }
        except Exception as err:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            logger.warning("OmniRoute gateway health check failed", error=str(err))
            return {
                "status": "unhealthy",
                "provider": "omniroute",
                "base_url": self._base_url,
                "latency_ms": round(latency_ms, 2),
                "error": str(err),
            }

    async def close(self) -> None:
        """Close the underlying HTTP client if created internally."""
        if not self._external_client:
            await self._client.aclose()
