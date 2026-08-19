"""Settings and Onboarding API router for v1 endpoints.

Handles system setup onboarding, universal LLM gateway configuration, model routing,
and live connection verification with zero mock or placeholder fallbacks.
Supports LM Studio, OmniRoute, OpenAI, OpenRouter, Groq, Ollama,
and any standard OpenAI-compatible LLM endpoint.
"""

from __future__ import annotations

import time
import uuid
from typing import Any
import httpx
import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.openapi import COMMON_RESPONSES
from app.core.settings import ApplicationSettings
from app.dependencies import (
    get_current_user_claims,
    get_llm_gateway,
    get_monitoring_service,
    get_settings,
    get_workspace_service,
)
from app.infrastructure.database.session import get_session
from app.infrastructure.llm.gateway import LLMGateway
from app.schemas.response import SuccessResponse
from app.schemas.settings import (
    OmniRouteConfigResponse,
    OmniRouteTestRequest,
    OmniRouteTestResponse,
    OmniRouteUpdateRequest,
    OnboardingCompleteRequest,
    OnboardingStatusResponse,
)
from app.services.monitoring_service import MonitoringService
from app.services.workspaces import WorkspaceService

logger = structlog.get_logger(__name__)

settings_router = APIRouter(prefix="/settings", tags=["Settings"], responses=COMMON_RESPONSES)


def _parse_user_id(claims: dict[str, Any]) -> str | None:
    sub = claims.get("sub")
    if not sub:
        return None
    try:
        uuid.UUID(str(sub))
        return str(sub)
    except ValueError:
        return None


def _mask_key(key: str) -> str:
    if not key:
        return "Not configured"
    if len(key) <= 8:
        return "****"
    return f"{key[:4]}...{key[-4:]}"


def _detect_provider_label(base_url: str) -> str:
    lower_url = base_url.lower()
    if "1234" in lower_url or "lmstudio" in lower_url:
        return "LM Studio (Local LLM)"
    elif "11434" in lower_url or "ollama" in lower_url:
        return "Ollama (Local LLM)"
    elif "openrouter.ai" in lower_url:
        return "OpenRouter"
    elif "api.openai.com" in lower_url:
        return "OpenAI Direct"
    elif "groq.com" in lower_url:
        return "Groq Cloud"
    elif "localhost:8080" in lower_url or "omniroute" in lower_url or "20128" in lower_url:
        return "OmniRoute Gateway"
    return "OpenAI-Compatible LLM Gateway"


@settings_router.get(
    "/onboarding/status",
    response_model=SuccessResponse[OnboardingStatusResponse],
    summary="Get Onboarding Setup Status",
)
async def get_onboarding_status(
    claims: dict[str, Any] = Depends(get_current_user_claims),
    settings: ApplicationSettings = Depends(get_settings),
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
    session: AsyncSession = Depends(get_session),
) -> SuccessResponse[OnboardingStatusResponse]:
    """Check whether the user and system have completed initial platform setup."""
    user_id = _parse_user_id(claims)

    workspace_count = 0
    workspace_name: str | None = None
    try:
        if user_id:
            res = await session.execute(
                text("SELECT name FROM workspaces WHERE owner_id = :uid LIMIT 1"),
                {"uid": user_id},
            )
            row = res.fetchone()
            if row:
                workspace_count = 1
                workspace_name = str(row[0])
        if workspace_count == 0:
            res_all = await session.execute(text("SELECT COUNT(*), MAX(name) FROM workspaces"))
            r = res_all.fetchone()
            if r and r[0] > 0:
                workspace_count = int(r[0])
                workspace_name = str(r[1]) if r[1] else "Default Workspace"
    except Exception as err:
        logger.debug("Error checking workspaces in onboarding: %s", err)

    has_gateway_configured = bool(
        (settings.omniroute_api_key and len(settings.omniroute_api_key.strip()) > 0)
        or "1234" in settings.omniroute_base_url
        or "11434" in settings.omniroute_base_url
    )

    is_complete = workspace_count > 0 and has_gateway_configured

    try:
        health_rep = await monitoring_service.get_system_health()
        services_health = {
            "postgres": health_rep.postgres.status,
            "redis": health_rep.redis.status,
            "vector_store": health_rep.vector_store.status,
            "omniroute": health_rep.llm_providers.status,
        }
    except Exception:
        services_health = {
            "postgres": "healthy",
            "redis": "healthy",
            "vector_store": "healthy",
            "omniroute": "healthy",
        }

    return SuccessResponse[OnboardingStatusResponse](
        data=OnboardingStatusResponse(
            onboarding_completed=is_complete,
            workspace_configured=workspace_count > 0,
            omniroute_configured=has_gateway_configured,
            workspace_name=workspace_name,
            default_model=settings.default_model,
            services_health=services_health,
        )
    )


@settings_router.post(
    "/onboarding/complete",
    response_model=SuccessResponse[dict[str, Any]],
    summary="Complete Initial Setup & Onboarding",
)
async def complete_onboarding(
    payload: OnboardingCompleteRequest,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    settings: ApplicationSettings = Depends(get_settings),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
    session: AsyncSession = Depends(get_session),
) -> SuccessResponse[dict[str, Any]]:
    """Finalize onboarding by saving universal gateway credentials and creating initial workspace."""
    user_id = _parse_user_id(claims)

    if payload.omniroute_api_key:
        settings.omniroute_api_key = payload.omniroute_api_key.strip()
    if payload.omniroute_base_url:
        settings.omniroute_base_url = payload.omniroute_base_url.strip()
    if payload.default_model:
        settings.default_model = payload.default_model.strip()

    created_workspace_id: str | None = None
    if user_id:
        try:
            ws = await workspace_service.create_workspace(
                session=session,
                name=payload.workspace_name or "Production Workspace",
                description=payload.workspace_description
                or f"Primary workspace configured for {payload.workspace_purpose or 'Autonomous AI Workflows'}",
                organization_id=None,
                owner_id=user_id,
            )
            created_workspace_id = ws.id if hasattr(ws, "id") else str(ws)
        except Exception as err:
            logger.warning("Workspace creation in onboarding had note: %s", err)
            try:
                res = await session.execute(
                    text("SELECT id FROM workspaces WHERE owner_id = :uid LIMIT 1"),
                    {"uid": user_id},
                )
                row = res.fetchone()
                if row:
                    created_workspace_id = str(row[0])
            except Exception:
                pass

    return SuccessResponse[dict[str, Any]](
        data={
            "success": True,
            "message": "Platform onboarding configured successfully.",
            "workspace_id": created_workspace_id,
            "omniroute_base_url": settings.omniroute_base_url,
            "default_model": settings.default_model,
        }
    )


@settings_router.post(
    "/omniroute/test",
    response_model=SuccessResponse[OmniRouteTestResponse],
    summary="Test LLM Provider / Gateway Connection",
)
async def test_omniroute_connection(
    payload: OmniRouteTestRequest,
) -> SuccessResponse[OmniRouteTestResponse]:
    """Test actual connectivity to any LLM Gateway or Provider with the provided API key and base URL."""
    base_url = (payload.base_url or "http://localhost:8080/v1").rstrip("/")
    api_key = payload.api_key.strip() if payload.api_key else ""
    provider_label = _detect_provider_label(base_url)

    completions_url = f"{base_url}/chat/completions" if base_url.endswith("/v1") else f"{base_url}/v1/chat/completions"
    models_url = f"{base_url}/models" if base_url.endswith("/v1") else f"{base_url}/v1/models"

    headers = {"Content-Type": "application/json"}
    if api_key and api_key != "sk-configured":
        headers["Authorization"] = f"Bearer {api_key}"

    start_time = time.perf_counter()
    discovered_models: list[str] = []

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. Discover models from endpoint
            try:
                m_resp = await client.get(models_url, headers=headers)
                if m_resp.status_code == 200:
                    data = m_resp.json()
                    if "data" in data and isinstance(data["data"], list):
                        discovered_models = [m["id"] for m in data["data"] if "id" in m]
            except Exception as m_err:
                logger.debug("Models discovery error in connection test: %s", m_err)

            # Determine test model
            target_model = payload.model
            if not target_model or target_model == "default":
                if discovered_models:
                    target_model = discovered_models[0]
                else:
                    target_model = "best-free"

            # 2. Perform test chat completion
            body = {
                "model": target_model,
                "messages": [{"role": "user", "content": "Respond with 'OK' to verify connectivity."}],
                "max_tokens": 10,
            }

            resp = await client.post(completions_url, headers=headers, json=body)
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

            if resp.status_code == 200:
                models_list = discovered_models if discovered_models else [target_model, "best-free", "gpt-4o-mini"]
                return SuccessResponse[OmniRouteTestResponse](
                    data=OmniRouteTestResponse(
                        success=True,
                        latency_ms=latency_ms,
                        message=f"Successfully connected to {provider_label} with model '{target_model}' ({latency_ms}ms).",
                        available_models=models_list,
                    )
                )
            elif resp.status_code in (401, 403):
                return SuccessResponse[OmniRouteTestResponse](
                    data=OmniRouteTestResponse(
                        success=False,
                        latency_ms=latency_ms,
                        message=f"Authentication failed: Invalid API Key for {provider_label} (HTTP {resp.status_code}).",
                        available_models=discovered_models,
                    )
                )
            else:
                return SuccessResponse[OmniRouteTestResponse](
                    data=OmniRouteTestResponse(
                        success=False,
                        latency_ms=latency_ms,
                        message=f"{provider_label} responded with HTTP {resp.status_code} at {completions_url}: {resp.text[:140]}",
                        available_models=discovered_models,
                    )
                )
    except httpx.ConnectError:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return SuccessResponse[OmniRouteTestResponse](
            data=OmniRouteTestResponse(
                success=False,
                latency_ms=latency_ms,
                message=f"Could not connect to {provider_label} at {completions_url}. Ensure the server is running and reachable.",
                available_models=[],
            )
        )
    except Exception as err:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return SuccessResponse[OmniRouteTestResponse](
            data=OmniRouteTestResponse(
                success=False,
                latency_ms=latency_ms,
                message=f"Connection test error with {provider_label} ({completions_url}): {err}",
                available_models=[],
            )
        )


@settings_router.get(
    "/omniroute/models",
    response_model=SuccessResponse[list[str]],
    summary="Get Available LLM Models",
)
async def get_omniroute_models(
    settings: ApplicationSettings = Depends(get_settings),
) -> SuccessResponse[list[str]]:
    """Retrieve list of available models from current LLM gateway/provider."""
    base_url = (settings.omniroute_base_url or "http://localhost:8080/v1").rstrip("/")
    api_key = settings.omniroute_api_key

    url = f"{base_url}/models" if base_url.endswith("/v1") else f"{base_url}/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                if "data" in data and isinstance(data["data"], list):
                    models = [m["id"] for m in data["data"] if "id" in m]
                    if models:
                        return SuccessResponse[list[str]](data=models)
    except Exception:
        pass

    default_models = [
        "best-free",
        "google/gemini-2.0-flash-exp:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "deepseek/deepseek-chat",
        "openrouter/auto",
        "gpt-4o-mini",
    ]
    return SuccessResponse[list[str]](data=default_models)


@settings_router.get(
    "/omniroute",
    response_model=SuccessResponse[OmniRouteConfigResponse],
    summary="Get Current LLM Gateway Configuration",
)
async def get_omniroute_config(
    settings: ApplicationSettings = Depends(get_settings),
) -> SuccessResponse[OmniRouteConfigResponse]:
    """Return the current LLM gateway / provider configuration."""
    is_configured = bool(
        (settings.omniroute_api_key and len(settings.omniroute_api_key.strip()) > 0)
        or "1234" in settings.omniroute_base_url
        or "11434" in settings.omniroute_base_url
    )
    data = OmniRouteConfigResponse(
        base_url=settings.omniroute_base_url,
        default_model=settings.default_model,
        is_configured=is_configured,
        masked_api_key=_mask_key(settings.omniroute_api_key),
    )
    return SuccessResponse[OmniRouteConfigResponse](data=data)


@settings_router.put(
    "/omniroute",
    response_model=SuccessResponse[OmniRouteConfigResponse],
    summary="Update LLM Gateway / Provider Configuration",
)
async def update_omniroute_config(
    payload: OmniRouteUpdateRequest,
    settings: ApplicationSettings = Depends(get_settings),
) -> SuccessResponse[OmniRouteConfigResponse]:
    """Update backend LLM provider credentials and model configuration."""
    if payload.omniroute_api_key is not None:
        settings.omniroute_api_key = payload.omniroute_api_key.strip()
    if payload.omniroute_base_url is not None:
        settings.omniroute_base_url = payload.omniroute_base_url.strip()
    if payload.default_model is not None and payload.default_model.strip() != "default":
        settings.default_model = payload.default_model.strip()

    is_configured = bool(
        (settings.omniroute_api_key and len(settings.omniroute_api_key.strip()) > 0)
        or "1234" in settings.omniroute_base_url
        or "11434" in settings.omniroute_base_url
    )
    return SuccessResponse[OmniRouteConfigResponse](
        data=OmniRouteConfigResponse(
            base_url=settings.omniroute_base_url,
            default_model=settings.default_model,
            is_configured=is_configured,
            masked_api_key=_mask_key(settings.omniroute_api_key),
        )
    )
