"""Role-to-permission mapping registry and policy evaluation engine.

Centralizes mapping between Organization/Workspace roles and granular string
permissions.
"""

from __future__ import annotations

from app.authorization.permissions import (
    AGENT_CREATE,
    AGENT_DELETE,
    AGENT_EXECUTE,
    AGENT_READ,
    AGENT_UPDATE,
    ALL_PERMISSIONS,
    API_KEY_CREATE,
    API_KEY_DELETE,
    API_KEY_READ,
    KNOWLEDGE_DELETE,
    KNOWLEDGE_READ,
    KNOWLEDGE_WRITE,
    ORGANIZATION_DELETE,
    ORGANIZATION_MANAGE_MEMBERS,
    ORGANIZATION_READ,
    ORGANIZATION_UPDATE,
    WORKFLOW_CREATE,
    WORKFLOW_DELETE,
    WORKFLOW_EXECUTE,
    WORKFLOW_READ,
    WORKFLOW_UPDATE,
    WORKSPACE_CREATE,
    WORKSPACE_DELETE,
    WORKSPACE_MANAGE_MEMBERS,
    WORKSPACE_READ,
    WORKSPACE_UPDATE,
)
from app.authorization.roles import UserRole, WorkspaceRole

ORG_ROLE_PERMISSIONS: dict[str, set[str]] = {
    UserRole.OWNER.value: set(ALL_PERMISSIONS),
    UserRole.ADMIN.value: (ALL_PERMISSIONS - {ORGANIZATION_DELETE})
    | {ORGANIZATION_UPDATE, ORGANIZATION_MANAGE_MEMBERS},
    UserRole.MEMBER.value: {
        ORGANIZATION_READ,
        WORKSPACE_READ,
        WORKSPACE_CREATE,
        WORKFLOW_READ,
        WORKFLOW_CREATE,
        WORKFLOW_EXECUTE,
        AGENT_READ,
        AGENT_EXECUTE,
        KNOWLEDGE_READ,
        KNOWLEDGE_WRITE,
    },
    UserRole.VIEWER.value: {
        ORGANIZATION_READ,
        WORKSPACE_READ,
        WORKFLOW_READ,
        AGENT_READ,
        KNOWLEDGE_READ,
    },
}

WORKSPACE_ROLE_PERMISSIONS: dict[str, set[str]] = {
    WorkspaceRole.OWNER.value: {
        WORKSPACE_READ,
        WORKSPACE_UPDATE,
        WORKSPACE_DELETE,
        WORKSPACE_MANAGE_MEMBERS,
        WORKFLOW_READ,
        WORKFLOW_CREATE,
        WORKFLOW_UPDATE,
        WORKFLOW_EXECUTE,
        WORKFLOW_DELETE,
        AGENT_READ,
        AGENT_CREATE,
        AGENT_UPDATE,
        AGENT_EXECUTE,
        AGENT_DELETE,
        KNOWLEDGE_READ,
        KNOWLEDGE_WRITE,
        KNOWLEDGE_DELETE,
        API_KEY_READ,
        API_KEY_CREATE,
        API_KEY_DELETE,
    },
    WorkspaceRole.ADMIN.value: {
        WORKSPACE_READ,
        WORKSPACE_UPDATE,
        WORKSPACE_MANAGE_MEMBERS,
        WORKFLOW_READ,
        WORKFLOW_CREATE,
        WORKFLOW_UPDATE,
        WORKFLOW_EXECUTE,
        WORKFLOW_DELETE,
        AGENT_READ,
        AGENT_CREATE,
        AGENT_UPDATE,
        AGENT_EXECUTE,
        KNOWLEDGE_READ,
        KNOWLEDGE_WRITE,
        API_KEY_READ,
        API_KEY_CREATE,
    },
    WorkspaceRole.EDITOR.value: {
        WORKSPACE_READ,
        WORKFLOW_READ,
        WORKFLOW_CREATE,
        WORKFLOW_UPDATE,
        WORKFLOW_EXECUTE,
        AGENT_READ,
        AGENT_CREATE,
        AGENT_UPDATE,
        AGENT_EXECUTE,
        KNOWLEDGE_READ,
        KNOWLEDGE_WRITE,
    },
    WorkspaceRole.CONTRIBUTOR.value: {
        WORKSPACE_READ,
        WORKFLOW_READ,
        WORKFLOW_EXECUTE,
        AGENT_READ,
        AGENT_EXECUTE,
        KNOWLEDGE_READ,
        KNOWLEDGE_WRITE,
    },
    WorkspaceRole.VIEWER.value: {
        WORKSPACE_READ,
        WORKFLOW_READ,
        AGENT_READ,
        KNOWLEDGE_READ,
    },
}


def get_permissions_for_org_role(role: str | UserRole) -> set[str]:
    """Get the set of granted permissions for an Organization role.

    Args:
        role: Organization role string or UserRole enum.

    Returns:
        Set of permission strings.
    """
    key = role.value if isinstance(role, UserRole) else str(role).lower()
    return ORG_ROLE_PERMISSIONS.get(key, set())


def get_permissions_for_workspace_role(role: str | WorkspaceRole) -> set[str]:
    """Get the set of granted permissions for a Workspace role.

    Args:
        role: Workspace role string or WorkspaceRole enum.

    Returns:
        Set of permission strings.
    """
    key = role.value if isinstance(role, WorkspaceRole) else str(role).lower()
    return WORKSPACE_ROLE_PERMISSIONS.get(key, set())
