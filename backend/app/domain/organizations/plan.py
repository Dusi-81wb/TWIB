"""Subscription plan enumeration.

A :class:`SubscriptionPlan` is the immutable, string-valued representation of
the subscription plan an organization is on. Only the plans themselves are
modelled here; billing logic is intentionally out of scope.
"""

from __future__ import annotations

from enum import StrEnum


class SubscriptionPlan(StrEnum):
    """The subscription plans an organization can be on.

    Members:
        FREE: The free tier.
        STARTER: The starter plan.
        PROFESSIONAL: The professional plan.
        ENTERPRISE: The enterprise plan.
        CUSTOM: A custom-negotiated plan.
    """

    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"
