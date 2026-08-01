# Config

## Purpose

Centralized configuration management using Pydantic Settings. Single source of truth for all environment-specific settings.

## Responsibilities

- Load configuration from environment variables
- Validate configuration at startup
- Provide typed access to settings
- Support multiple environments (dev, staging, prod)
- Manage secrets securely

## What Belongs Here

- Pydantic `BaseSettings` classes
- Environment-specific overrides
- Configuration validation logic
- Feature flags

## What Must NEVER Belong Here

- Business logic
- Database connections
- Hardcoded secrets
- Runtime mutable state

## Dependencies

- `pydantic-settings`
- Environment variables (none

## Future Phases

- Phase 1: Base configuration
- Phase 2: Auth configuration
- Phase 3: Database configuration
- Phase 5: LLM provider configuration
- Phase 11: Payment configuration