"""OpenAPI metadata and schema customization for the TWIB API.

Centralizes API descriptions, contact, license, tag list, common error responses,
and custom OpenAPI schema generation for SDK readiness.
"""

from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.api.tags import (
    ADMIN,
    AGENTS,
    ANALYTICS,
    API_KEYS,
    AUDIT,
    AUTHENTICATION,
    BILLING,
    HEALTH,
    INVITATIONS,
    MONITORING,
    ORGANIZATIONS,
    STORAGE,
    USERS,
    WORKFLOWS,
    WORKSPACES,
)
from app.core.constants import SERVICE_NAME, VERSION

DESCRIPTION = """
# TWIB — Total Workflow Intelligence Builder API

The TWIB API provides enterprise AI-native capabilities:

- **Authentication**: JWT token refresh, session management, RBAC, API keys.
- **Organizations**: Multi-tenant isolation, accounts, membership, invitations.
- **Agents**: Planner, Research, Analyst, Architect, Validator, Optimizer, Docs.
- **Workflows**: Generation, step execution, state persistence, checkpoints, templates.
- **Realtime**: Live WebSocket telemetry streaming (`/ws/workflows/{workflow_id}`).
- **Monitoring**: System health, workflow telemetry, and performance metrics.

## Response Envelope Standard

All REST API endpoints return consistent response envelopes:

- **Success Envelope**: `{"success": true, "data": ...}`
- **Error Envelope**: `{"success": false, "error": {"code": ..., "message": ...}}`

## Authentication

All protected endpoints require a Bearer JWT Token in the `Authorization` header:

```http
Authorization: Bearer <your_jwt_access_token>
```
"""

CONTACT = {
    "name": "TWIB API Support Team",
    "url": "https://github.com/Dusi-81wb/TWIB",
    "email": "support@twib.ai",
}

LICENSE = {
    "name": "MIT License",
    "url": "https://opensource.org/licenses/MIT",
}

OPENAPI_TAGS = [
    {"name": HEALTH, "description": "Service health and liveness checks."},
    {"name": AUTHENTICATION, "description": "Identity and session management."},
    {"name": USERS, "description": "User account management and profiles."},
    {"name": ORGANIZATIONS, "description": "Organization tenant management."},
    {"name": WORKSPACES, "description": "Workspace collaboration boundaries."},
    {"name": INVITATIONS, "description": "Workspace invitations and membership."},
    {"name": API_KEYS, "description": "Workspace API key creation and revocation."},
    {"name": AUDIT, "description": "Security audit logging and compliance records."},
    {
        "name": WORKFLOWS,
        "description": "Workflow creation, execution, checkpoints, templates.",
    },
    {
        "name": MONITORING,
        "description": "System health, workflow telemetry, and agent metrics.",
    },
    {
        "name": AGENTS,
        "description": "AI agent execution and collaborative orchestration.",
    },
    {"name": BILLING, "description": "Subscriptions, usage plans, and invoices."},
    {"name": ADMIN, "description": "Platform administration and system operations."},
    {"name": ANALYTICS, "description": "Usage metrics and system reporting."},
    {"name": STORAGE, "description": "Object storage, file uploads, and assets."},
]

COMMON_RESPONSES: dict[int | str, dict[str, Any]] = {
    400: {
        "description": "Bad Request — Invalid parameters or malformed payload.",
    },
    401: {
        "description": "Unauthorized — Authentication token missing or invalid.",
    },
    403: {
        "description": "Forbidden — Insufficient permissions.",
    },
    404: {
        "description": "Not Found — Requested resource does not exist.",
    },
    409: {
        "description": "Conflict — Resource state conflict or version mismatch.",
    },
    422: {
        "description": "Unprocessable Entity — Payload failed validation.",
    },
    500: {
        "description": "Internal Server Error — Unexpected backend failure.",
    },
}


def setup_openapi(app: FastAPI) -> None:
    """Configure custom OpenAPI schema generator for TWIB API.

    Injects JWT Bearer security scheme, organizes tag specifications, and sets up
    reusable OpenAPI metadata for external client and SDK code generator readiness.
    """

    def custom_openapi() -> dict[str, Any]:
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=SERVICE_NAME,
            version=VERSION,
            description=DESCRIPTION,
            routes=app.routes,
            tags=OPENAPI_TAGS,
            license_info=LICENSE,
            contact=CONTACT,
        )

        components = openapi_schema.setdefault("components", {})
        security_schemes = components.setdefault("securitySchemes", {})
        security_schemes["BearerAuth"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter JWT access token to authenticate requests.",
        }

        # Apply JWT Bearer security scheme globally (except public health route)
        openapi_schema["security"] = [{"BearerAuth": []}]

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi  # type: ignore[method-assign]
