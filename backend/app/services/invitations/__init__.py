"""Invitation services package.

Provides the application service for workspace invitations:

- :class:`.InvitationService`: Invitation creation, acceptance, and rejection.
"""

from app.services.invitations.invitation_service import InvitationService

__all__ = ["InvitationService"]
