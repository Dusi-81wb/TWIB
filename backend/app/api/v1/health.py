"""Health check endpoints for API version 1."""

from typing import Any

from fastapi import APIRouter, Depends

from app.core.constants import SERVICE_NAME, VERSION
from app.core.settings import ApplicationSettings
from app.dependencies import get_llm_gateway, get_settings
from app.infrastructure.llm.gateway import LLMGateway

health_router = APIRouter()


@health_router.get("/health")
def get_health() -> dict[str, str]:
    """Return the current health status of the service.

    Returns:
        A dictionary describing the service health, name, and version.
    """
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": VERSION,
    }


@health_router.get("/system/health")
async def get_system_health(
    gateway: LLMGateway = Depends(get_llm_gateway),
    settings: ApplicationSettings = Depends(get_settings),
) -> dict[str, Any]:
    """Return system health metrics including OmniRoute gateway status.

    Returns:
        System health details including OmniRoute connectivity, latency, and model.
    """
    gw_health = await gateway.health()

    is_connected = gw_health.get("status") == "healthy"
    status_str = "Connected" if is_connected else "Disconnected"
    latency = gw_health.get("latency_ms", 0.0)

    model_name = getattr(gateway, "default_model", settings.default_model)
    base_url = getattr(gateway, "base_url", settings.omniroute_base_url)

    return {
        "status": "healthy" if is_connected else "degraded",
        "service": SERVICE_NAME,
        "version": VERSION,
        "services": {
            "omniroute": {
                "status": status_str,
                "connected": is_connected,
                "latency_ms": latency,
                "configured_model": model_name,
                "base_url": base_url,
            }
        },
    }
