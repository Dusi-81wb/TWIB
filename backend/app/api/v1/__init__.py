"""API version 1 package."""

from fastapi import APIRouter

from app.api.v1.agents import agents_router
from app.api.v1.api_keys import api_keys_router
from app.api.v1.audit import audit_router
from app.api.v1.auth import auth_router
from app.api.v1.health import health_router
from app.api.v1.invitations import invitations_router
from app.api.v1.monitoring import monitoring_router
from app.api.v1.organizations import organizations_router
from app.api.v1.users import users_router
from app.api.v1.websockets import websockets_router
from app.api.v1.workflows import workflows_router
from app.api.v1.workspaces import workspaces_router
from app.core.constants import API_V1_PREFIX

api_v1_router = APIRouter(prefix=API_V1_PREFIX)
api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(api_keys_router)
api_v1_router.include_router(audit_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(organizations_router)
api_v1_router.include_router(workspaces_router)
api_v1_router.include_router(invitations_router)
api_v1_router.include_router(workflows_router)
api_v1_router.include_router(agents_router)
api_v1_router.include_router(websockets_router)
api_v1_router.include_router(monitoring_router)

__all__ = ["api_v1_router"]
