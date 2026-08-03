"""API version 1 package."""

from fastapi import APIRouter

from app.api.v1.api_keys import api_keys_router
from app.api.v1.audit import audit_router
from app.api.v1.auth import auth_router
from app.api.v1.health import health_router
from app.core.constants import API_V1_PREFIX

api_v1_router = APIRouter(prefix=API_V1_PREFIX)
api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(api_keys_router)
api_v1_router.include_router(audit_router)

__all__ = ["api_v1_router"]
