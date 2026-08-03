"""Invitation application service.

Manages workspace invitation lifecycle (creation, acceptance, rejection).
Integrates with Unit of Work and WorkspaceService to persist membership when
accepted.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from app.domain.exceptions import BusinessRuleViolation, EntityNotFound
from app.domain.repositories.unit_of_work import UnitOfWork
from app.domain.value_objects import UuidIdentity
from app.services.workspaces.workspace_service import WorkspaceService


class InvitationService:
    """Service managing workspace invitation lifecycle.

    Attributes:
        _uow: Unit of Work for repository access.
        _workspace_service: WorkspaceService instance for updating membership
            upon acceptance.
        _invitations: In-memory registry for stored invitations.
    """

    def __init__(
        self,
        unit_of_work: UnitOfWork,
        workspace_service: WorkspaceService | None = None,
    ) -> None:
        """Initialize the invitation service.

        Args:
            unit_of_work: Unit of Work for repository access.
            workspace_service: Optional WorkspaceService instance.
        """
        self._uow = unit_of_work
        self._workspace_service = workspace_service or WorkspaceService(unit_of_work)
        self._invitations: dict[str, dict[str, Any]] = {}

    async def create_invitation(
        self,
        workspace_id: str,
        email: str,
        role: str = "viewer",
        inviter_id: str = "",
    ) -> dict[str, Any]:
        """Create a new workspace invitation.

        Args:
            workspace_id: Target workspace UUID string.
            email: Invitee email address string.
            role: Assigned workspace role string.
            inviter_id: Inviter user UUID string.

        Returns:
            Dict representing the stored invitation details.

        Raises:
            EntityNotFound: If workspace does not exist.
            BusinessRuleViolation: If role or payload is invalid.
        """
        try:
            ws_uuid = uuid.UUID(workspace_id)
        except ValueError as err:
            raise EntityNotFound(f"Workspace '{workspace_id}' not found") from err

        async with self._uow as uow:
            ws = await uow.workspaces.find_by_id(UuidIdentity(ws_uuid))
            if ws is None:
                raise EntityNotFound(f"Workspace '{workspace_id}' not found")

        invitation_id = str(uuid.uuid4())
        record = {
            "id": invitation_id,
            "workspace_id": workspace_id,
            "email": email.strip().lower(),
            "role": role.lower(),
            "status": "pending",
            "inviter_id": inviter_id,
            "created_at": datetime.now(UTC).isoformat(),
        }
        self._invitations[invitation_id] = record
        return record

    async def accept_invitation(
        self,
        invitation_id: str,
        user_id: str,
    ) -> dict[str, Any]:
        """Accept a pending workspace invitation and add member to workspace.

        Args:
            invitation_id: Invitation UUID string.
            user_id: Authenticated user UUID string.

        Returns:
            Updated invitation record dict.

        Raises:
            EntityNotFound: If invitation does not exist.
            BusinessRuleViolation: If invitation is not pending.
        """
        record = self._invitations.get(invitation_id)
        if record is None:
            raise EntityNotFound(f"Invitation '{invitation_id}' not found")

        if record["status"] != "pending":
            raise BusinessRuleViolation(f"Invitation is already {record['status']}")

        # Add user to the workspace via WorkspaceService
        await self._workspace_service.add_member(
            workspace_id=record["workspace_id"],
            user_id=user_id,
            role=record["role"],
        )

        record["status"] = "accepted"
        return record

    async def reject_invitation(
        self,
        invitation_id: str,
        user_id: str,
    ) -> dict[str, Any]:
        """Reject a pending workspace invitation.

        Args:
            invitation_id: Invitation UUID string.
            user_id: Authenticated user UUID string.

        Returns:
            Updated invitation record dict.

        Raises:
            EntityNotFound: If invitation does not exist.
            BusinessRuleViolation: If invitation is not pending.
        """
        record = self._invitations.get(invitation_id)
        if record is None:
            raise EntityNotFound(f"Invitation '{invitation_id}' not found")

        if record["status"] != "pending":
            raise BusinessRuleViolation(f"Invitation is already {record['status']}")

        record["status"] = "rejected"
        return record

    async def get_invitation(self, invitation_id: str) -> dict[str, Any]:
        """Retrieve an invitation by ID.

        Args:
            invitation_id: Invitation UUID string.

        Returns:
            Invitation record dict.

        Raises:
            EntityNotFound: If invitation does not exist.
        """
        record = self._invitations.get(invitation_id)
        if record is None:
            raise EntityNotFound(f"Invitation '{invitation_id}' not found")
        return record
