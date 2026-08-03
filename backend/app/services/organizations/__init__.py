"""Organization services package.

Provides the application service for organization management:

- :class:`.OrganizationService`: Organization CRUD operations.
"""

from app.services.organizations.organization_service import OrganizationService

__all__ = ["OrganizationService"]
