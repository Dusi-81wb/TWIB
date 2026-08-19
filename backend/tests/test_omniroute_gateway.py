"""Unit and integration tests for OmniRouteGateway and LLM Gateway abstractions."""

import httpx
import pytest

from app.container import ApplicationContainer
from app.core.settings import ApplicationSettings
from app.infrastructure.llm.exceptions import (
    GatewayAuthError,
    GatewayTimeoutError,
    GatewayUnavailableError,
)
from app.infrastructure.llm.gateway import LLMGateway
from app.infrastructure.llm.message import ChatMessage, MessageRole
from app.infrastructure.llm.models import GatewayResponse, GatewayUsage
from app.infrastructure.llm.omniroute_gateway import OmniRouteGateway


@pytest.fixture
def test_settings() -> ApplicationSettings:
    """Fixture providing ApplicationSettings with OmniRoute defaults."""
    return ApplicationSettings(
        omniroute_base_url="http://localhost:8080/v1",
        omniroute_api_key="test-api-key",
        default_model="gpt-4o",
    )


@pytest.mark.asyncio
async def test_omniroute_gateway_chat_success(
    test_settings: ApplicationSettings,
) -> None:
    """Test successful chat completion returning TWIB GatewayResponse."""

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/chat/completions"
        assert request.headers.get("Authorization") == "Bearer test-api-key"
        payload = request.read().decode("utf-8")
        assert "gpt-4o" in payload
        assert "Hello AI" in payload

        return httpx.Response(
            200,
            json={
                "id": "chatcmpl-123",
                "object": "chat.completion",
                "model": "gpt-4o",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "Hello human, how can I help?",
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 8,
                    "total_tokens": 18,
                },
            },
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        gateway = OmniRouteGateway(settings=test_settings, http_client=http_client)

        messages = [
            ChatMessage(role=MessageRole.USER, content="Hello AI"),
        ]
        response = await gateway.chat(
            messages,
            system_prompt="You are a helpful assistant",
            temperature=0.5,
        )

        assert isinstance(response, GatewayResponse)
        assert response.answer == "Hello human, how can I help?"
        assert response.provider == "omniroute"
        assert response.model == "gpt-4o"
        assert response.latency_ms >= 0.0
        assert isinstance(response.usage, GatewayUsage)
        assert response.usage.prompt_tokens == 10
        assert response.usage.completion_tokens == 8
        assert response.usage.total_tokens == 18


@pytest.mark.asyncio
async def test_omniroute_gateway_complete_success(
    test_settings: ApplicationSettings,
) -> None:
    """Test complete prompt shortcut method."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "model": "custom-model",
                "choices": [
                    {
                        "message": {"content": "Text completion answer."},
                    }
                ],
                "usage": {
                    "prompt_tokens": 5,
                    "completion_tokens": 5,
                    "total_tokens": 10,
                },
            },
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        gateway = OmniRouteGateway(settings=test_settings, http_client=http_client)
        response = await gateway.complete(
            "Generate code", model="custom-model", temperature=0.2
        )

        assert response.answer == "Text completion answer."
        assert response.model == "custom-model"
        assert response.provider == "omniroute"


@pytest.mark.asyncio
async def test_omniroute_gateway_auth_error(
    test_settings: ApplicationSettings,
) -> None:
    """Test authentication failure handling (HTTP 401)."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": "Invalid API key"})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        gateway = OmniRouteGateway(settings=test_settings, http_client=http_client)
        with pytest.raises(GatewayAuthError) as exc_info:
            await gateway.complete("Hello")

        assert exc_info.value.provider == "omniroute"
        assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_omniroute_gateway_server_unavailable(
    test_settings: ApplicationSettings,
) -> None:
    """Test server unavailable handling (HTTP 503)."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="Service Unavailable")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        gateway = OmniRouteGateway(settings=test_settings, http_client=http_client)
        with pytest.raises(GatewayUnavailableError) as exc_info:
            await gateway.complete("Hello")

        assert exc_info.value.provider == "omniroute"
        assert exc_info.value.status_code == 503


@pytest.mark.asyncio
async def test_omniroute_gateway_timeout(
    test_settings: ApplicationSettings,
) -> None:
    """Test request timeout handling."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("Request timed out", request=request)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        gateway = OmniRouteGateway(settings=test_settings, http_client=http_client)
        with pytest.raises(GatewayTimeoutError) as exc_info:
            await gateway.complete("Hello")

        assert exc_info.value.provider == "omniroute"


@pytest.mark.asyncio
async def test_omniroute_gateway_health_check(
    test_settings: ApplicationSettings,
) -> None:
    """Test gateway health check status reporting."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"data": [{"id": "gpt-4o"}]})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        gateway = OmniRouteGateway(settings=test_settings, http_client=http_client)
        health = await gateway.health()

        assert health["status"] == "healthy"
        assert health["provider"] == "omniroute"
        assert "latency_ms" in health


@pytest.mark.asyncio
async def test_di_container_llm_gateway_resolution(
    test_settings: ApplicationSettings,
) -> None:
    """Test that ApplicationContainer resolves llm_gateway singleton correctly."""
    container = ApplicationContainer()
    container.settings.override(test_settings)

    gateway = container.llm_gateway()
    assert isinstance(gateway, LLMGateway)
    assert isinstance(gateway, OmniRouteGateway)
    assert gateway.base_url == "http://localhost:8080/v1"
    assert gateway.default_model == "gpt-4o"
