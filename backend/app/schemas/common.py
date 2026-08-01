"""Reusable schema primitives shared across every API module.

The aliases in this module describe the types used repeatedly by response
and request schemas: entity identifiers, timestamps, and free-form
metadata. The :class:`TimestampedModel` base class adds the standard
creation and update timestamps to any schema that inherits from it.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, TypeAlias

from pydantic import BaseModel, Field

EntityId: TypeAlias = uuid.UUID
"""Alias for the universally unique identifier of an entity."""

Timestamp: TypeAlias = datetime
"""Alias for an absolute point in time."""

CreatedAt: TypeAlias = datetime
"""Alias for the timestamp at which a record was created."""

UpdatedAt: TypeAlias = datetime
"""Alias for the timestamp at which a record was last updated."""

Metadata: TypeAlias = dict[str, Any]
"""Alias for arbitrary key/value metadata attached to a record."""


class TimestampedModel(BaseModel):
    """Base model that adds creation and update timestamps.

    Attributes:
        created_at: Timestamp of record creation.
        updated_at: Timestamp of the last update.
    """

    created_at: CreatedAt = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of record creation.",
    )
    updated_at: UpdatedAt = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of the last update.",
    )
