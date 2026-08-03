"""Organization and Workspace role definitions and hierarchy ranking.

Re-exports domain role enumerations and provides rank comparison helpers for
hierarchical Role-Based Access Control (RBAC).
"""

from __future__ import annotations

from app.domain.users.role import UserRole as UserRole
from app.domain.workspaces.membership import WorkspaceRole as WorkspaceRole

__all__ = [
    "ORG_ROLE_RANKS",
    "WORKSPACE_ROLE_RANKS",
    "UserRole",
    "WorkspaceRole",
    "is_org_role_at_least",
    "is_workspace_role_at_least",
]

ORG_ROLE_RANKS: dict[str, int] = {
    UserRole.OWNER.value: 40,
    UserRole.ADMIN.value: 30,
    UserRole.MEMBER.value: 20,
    UserRole.VIEWER.value: 10,
}

WORKSPACE_ROLE_RANKS: dict[str, int] = {
    WorkspaceRole.OWNER.value: 50,
    WorkspaceRole.ADMIN.value: 40,
    WorkspaceRole.EDITOR.value: 30,
    WorkspaceRole.CONTRIBUTOR.value: 20,
    WorkspaceRole.VIEWER.value: 10,
}


def is_org_role_at_least(
    user_role: str | UserRole,
    required_role: str | UserRole,
) -> bool:
    """Check if an organization user role meets or exceeds a required rank.

    Args:
        user_role: The role held by the user.
        required_role: The minimum required role.

    Returns:
        True if user_role rank >= required_role rank, False otherwise.
    """
    user_val = user_role.value if isinstance(user_role, UserRole) else str(user_role)
    req_val = (
        required_role.value
        if isinstance(required_role, UserRole)
        else str(required_role)
    )

    user_rank = ORG_ROLE_RANKS.get(user_val.lower(), 0)
    req_rank = ORG_ROLE_RANKS.get(req_val.lower(), 999)

    return user_rank >= req_rank


def is_workspace_role_at_least(
    user_role: str | WorkspaceRole,
    required_role: str | WorkspaceRole,
) -> bool:
    """Check if a workspace role meets or exceeds a required rank.

    Args:
        user_role: The workspace role held by the user.
        required_role: The minimum required workspace role.

    Returns:
        True if user_role rank >= required_role rank, False otherwise.
    """
    user_val = (
        user_role.value
        if isinstance(user_role, WorkspaceRole)
        else str(user_role)
    )
    req_val = (
        required_role.value
        if isinstance(required_role, WorkspaceRole)
        else str(required_role)
    )

    user_rank = WORKSPACE_ROLE_RANKS.get(user_val.lower(), 0)
    req_rank = WORKSPACE_ROLE_RANKS.get(req_val.lower(), 999)

    return user_rank >= req_rank
