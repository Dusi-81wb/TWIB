"""User role enumeration.

A :class:`UserRole` is the immutable, string-valued representation of the role
a user holds inside an organization. Only the roles themselves are modelled
here; permissions are intentionally out of scope for this phase.
"""

from __future__ import annotations

from enum import StrEnum


class UserRole(StrEnum):
    """The domain roles a user can hold.

    Members:
        OWNER: The organization owner.
        ADMIN: An administrator of the organization.
        MEMBER: A regular member of the organization.
        VIEWER: A read-only viewer of the organization.
    """

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"
