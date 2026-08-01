"""Concrete domain value objects.

This package contains the reusable, framework-independent value objects of the
platform domain: identifiers, email addresses, names, slugs, timestamps,
URLs, versions, money, and metadata. Every value object is immutable, validates
its value at construction, and is compared by value.

All classes are pure Python (standard library only). The scalar value objects
inherit from :class:`app.domain.value_object.ValueObject`; the UUID identity
is a standalone value type modelled on the generic ``Identity``.
"""

from __future__ import annotations

from app.domain.value_objects.email import Email
from app.domain.value_objects.id import UuidIdentity
from app.domain.value_objects.metadata import Metadata
from app.domain.value_objects.money import Money
from app.domain.value_objects.name import Name
from app.domain.value_objects.slug import Slug
from app.domain.value_objects.timestamp import Timestamp
from app.domain.value_objects.url import Url
from app.domain.value_objects.version import Version

__all__ = [
    "Email",
    "Metadata",
    "Money",
    "Name",
    "Slug",
    "Timestamp",
    "Url",
    "UuidIdentity",
    "Version",
]
