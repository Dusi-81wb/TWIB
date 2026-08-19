"""Hierarchical Role-Based Access Control (RBAC) package.

Provides central permission definitions, organization/workspace role hierarchies,
policy mappings, authorization service evaluation, and FastAPI dependency guards:

- :mod:`.permissions`: Permission string constants.
- :mod:`.roles`: Organization & Workspace role enumerations.
- :mod:`.policy`: Central role-to-permission policy registry.
- :class:`.AuthorizationService`: Policy evaluator.
- :class:`.RequirePermission`: FastAPI permission guard.
- :class:`.RequireOrganizationRole`: Org role guard.
- :class:`.RequireWorkspaceRole`: Workspace role guard.
"""

from app.authorization.authorization_service import AuthorizationService
from app.authorization.decorators import (
    RequireOrganizationRole,
    RequirePermission,
    RequireWorkspaceRole,
    require_organization_role,
    require_permission,
    require_workspace_role,
)
from app.authorization.permissions import ALL_PERMISSIONS
from app.authorization.policy import (
    get_permissions_for_org_role,
    get_permissions_for_workspace_role,
)
from app.authorization.roles import (
    UserRole,
    WorkspaceRole,
    is_org_role_at_least,
    is_workspace_role_at_least,
)

__all__ = [
    "ALL_PERMISSIONS",
    "AuthorizationService",
    "RequireOrganizationRole",
    "RequirePermission",
    "RequireWorkspaceRole",
    "UserRole",
    "WorkspaceRole",
    "get_permissions_for_org_role",
    "get_permissions_for_workspace_role",
    "is_org_role_at_least",
    "is_workspace_role_at_least",
    "require_organization_role",
    "require_permission",
    "require_workspace_role",
]
