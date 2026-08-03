"""Centralized API tags.

Every endpoint group declares its OpenAPI tag from this single module so
tag names stay consistent across the whole API surface. These are constants
only; router wiring happens in later phases.
"""

HEALTH = "health"
AUTHENTICATION = "authentication"
USERS = "users"
ORGANIZATIONS = "organizations"
WORKFLOWS = "workflows"
AGENTS = "agents"
BILLING = "billing"
ADMIN = "admin"
ANALYTICS = "analytics"
API_KEYS = "api-keys"
AUDIT = "audit"
STORAGE = "storage"
