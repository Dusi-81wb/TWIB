"""OpenAPI metadata for the TWIB API.

Centralizes the API description, contact, license, and the ordered tag list
so the application factory stays free of inline metadata. Title and version
are resolved from :mod:`app.core.constants`.
"""

from app.api.tags import (
    ADMIN,
    AGENTS,
    ANALYTICS,
    AUTHENTICATION,
    BILLING,
    HEALTH,
    ORGANIZATIONS,
    STORAGE,
    USERS,
    WORKFLOWS,
)

DESCRIPTION = """
The TWIB (Total Workflow Intelligence Builder) API is the backend for an
enterprise AI-native platform that generates, analyzes, validates,
optimizes, and executes intelligent business workflows using collaborative
AI agents.

## Response Envelope

All responses follow a consistent envelope. Successful requests return
`{"success": true, "data": ...}` and failures return
`{"success": false, "error": {"code": ..., "message": ...}}`.
"""

CONTACT = {
    "name": "TWIB",
    "url": "https://github.com/Dusi-81wb/TWIB",
}

LICENSE = {
    "name": "MIT",
    "url": "https://opensource.org/licenses/MIT",
}

OPENAPI_TAGS = [
    {"name": HEALTH, "description": "Service health and liveness checks."},
    {"name": AUTHENTICATION, "description": "Identity, login, and session management."},
    {"name": USERS, "description": "User account management."},
    {"name": ORGANIZATIONS, "description": "Organization and workspace management."},
    {
        "name": WORKFLOWS,
        "description": "Workflow generation, execution, and monitoring.",
    },
    {"name": AGENTS, "description": "AI agent configuration and coordination."},
    {"name": BILLING, "description": "Subscriptions, plans, and invoices."},
    {"name": ADMIN, "description": "Platform administration and operations."},
    {"name": ANALYTICS, "description": "Usage metrics and reporting."},
    {"name": STORAGE, "description": "Object storage and file uploads."},
]
