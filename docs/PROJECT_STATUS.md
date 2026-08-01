# TWIB Project Status

> **Project:** TWIB (Total Workflow Intelligence Builder)
>
> **Document Type:** Living Project Status Dashboard
>
> **Status:** Active Development
>
> **Last Updated:** August 2026

---

# Project Overview

TWIB is an enterprise AI-native SaaS platform that generates, analyzes, validates, optimizes, and executes intelligent business workflows using multiple collaborative AI agents.

This document tracks the **current development state** of the project.

Unlike `roadmap.md`, which defines the long-term plan, this document represents the project's **current operational status**.

---

# Overall Progress

```
Architecture        ████████████████████ 100%

Documentation       ████████████████████ 100%

Foundation          ████████████████████ 100%

Domain Layer        █████████████████░░░░  85%

Authentication      ░░░░░░░░░░░░░░░░░░░░   0%

Database            ░░░░░░░░░░░░░░░░░░░░   0%

REST API            ░░░░░░░░░░░░░░░░░░░░   0%

LLM Layer           ░░░░░░░░░░░░░░░░░░░░   0%

Agents              ░░░░░░░░░░░░░░░░░░░░   0%

Workflow Engine     ░░░░░░░░░░░░░░░░░░░░   0%

Frontend            ░░░░░░░░░░░░░░░░░░░░   0%

Deployment          ░░░░░░░░░░░░░░░░░░░░   0%
```

> Domain Layer: Phases 2.1 (base classes, exceptions), 2.2 (concrete
> value objects), 2.3 (user domain), 2.4 (organization domain), and 2.5
> (workspace domain) are complete; repository interfaces follow in Phase 2.6.

---

# Current Sprint

Sprint 2

---

# Current Phase

Phase 2.6 — Repository Interfaces

---

# Current Status

🟢 Ready to Begin

---

# Current Objective

Define the repository interfaces for the domain aggregates (user, organization,
workspace) as framework-independent protocols, establishing the persistence
contracts application services depend on.

Do NOT implement

- Database models
- SQLAlchemy
- Repository implementations
- API routes
- Authentication

---

# Last Completed Milestone

✅ Phase 2.5

Completed

- `backend/app/domain/workspaces/` package with six files (`__init__.py`,
  `workspace.py`, `membership.py`, `settings.py`, `status.py`, `events.py`,
  `exceptions.py`)
- `Workspace` aggregate root built entirely from the Phase 2.2 value objects
  (`UuidIdentity`, `Name`, `Slug`, `Description`, `Timestamp`, `Metadata`,
  `Version`), the `WorkspaceStatus` enum, and the `WorkspaceSettings` domain
  object
- Immutable `WorkspaceMembership` domain object (user ID, workspace role,
  joined time, membership status, invitation-accepted flag) plus the
  `WorkspaceRole` `StrEnum` (owner, admin, editor, contributor, viewer) and
  `WorkspaceMembershipStatus` `StrEnum` (pending, active, inactive)
- Immutable `WorkspaceSettings` domain object (timezone, default language,
  visibility, AI model preference, execution limits, knowledge-base toggle,
  experimental-features toggle) plus the `WorkspaceVisibility` `StrEnum`
  (private, organization, public)
- `WorkspaceStatus` `StrEnum` (active, archived, suspended, deleted)
- Workspace domain events (`WorkspaceCreated`, `WorkspaceArchived`,
  `WorkspaceRenamed`, `WorkspaceOwnerChanged`, `WorkspaceMemberAdded`,
  `WorkspaceMemberRemoved`, `WorkspaceSettingsChanged`)
- Workspace business-rule exceptions (`InvalidWorkspaceState`,
  `WorkspaceArchived`, `WorkspaceAlreadyExists`, `DuplicateWorkspaceMember`,
  `OwnerCannotBeRemoved`)
- Domain methods (`rename`, `change_slug`, `change_description`, `change_owner`,
  `archive`, `restore`, `activate`, `suspend`, `add_member`, `remove_member`,
  `update_settings`, `update_metadata`, `increment_version`) that validate,
  record events, refresh `updated_at`, and auto-bump the optimistic-locking
  version
- The owner is implicitly added as an active OWNER-role member; the owner
  cannot be removed, and changing the owner swaps roles (new owner becomes
  OWNER, previous owner becomes ADMIN)
- Archived workspaces are immutable until restored; deleted workspaces cannot
  be modified
- New `Description` value object (`backend/app/domain/value_objects/description.py`)
  for free-text descriptions (max 500 characters; may be empty)
- Pure Python with no FastAPI, Pydantic, SQLAlchemy, repositories, billing,
  infrastructure, or authentication code
- `backend/README.md` documents the workspace aggregate, memberships, settings,
  statuses, domain events, and business-rule exceptions

(Previous: ✅ Phase 2.4)

---

# Next Milestone

Phase 2.6

Repository Interfaces

---

# Active Model

DeepSeek V4 Flash

(Current implementation model)

---

# Recommended Models

Architecture

Nemotron 3 Ultra

Backend

DeepSeek V4 Flash

AI

Qwen Coder

Testing

North Mini Code

Documentation

Nemotron

---

# Locked Decisions

These decisions must not change.

Backend

FastAPI

Frontend

Next.js

Database

PostgreSQL

ORM

SQLAlchemy

Cache

Redis

Vector Database

Qdrant

Authentication

JWT

OAuth2

RBAC

Deployment

Docker

Kubernetes

Architecture

Clean Architecture

Repository Pattern

Dependency Injection

Service Layer

Event Bus

Model Router

Workflow Engine

Agent Orchestrator

---

# Current Folder Structure

```
TWIB/

backend/
frontend/
agents/
workflows/
llm/
database/
auth/
cache/
payments/
storage/
analytics/
security/
deployment/
docker/
tests/
docs/
```

---

# Current Branch

main

---

# Last Stable Commit

_Not committed yet_

---

# Files Modified This Sprint

- backend/app/domain/value_objects/description.py (created)
- backend/app/domain/value_objects/__init__.py (exported `Description`)
- backend/app/domain/workspaces/__init__.py (created)
- backend/app/domain/workspaces/workspace.py (created)
- backend/app/domain/workspaces/membership.py (created)
- backend/app/domain/workspaces/settings.py (created)
- backend/app/domain/workspaces/status.py (created)
- backend/app/domain/workspaces/events.py (created)
- backend/app/domain/workspaces/exceptions.py (created)
- backend/README.md
- docs/PROJECT_STATUS.md

# Pending Tasks

## Phase 1.1

- [x] Initialize FastAPI
- [x] Application factory
- [x] Health endpoint
- [x] uv packaging and lockfile

## Phase 1.2

- [x] Configure Pydantic Settings
- [x] Environment-based configuration
- [x] Configuration validation
- [x] Application wiring

## Phase 1.3

- [x] Structured logging setup
- [x] JSON log output
- [x] Log level controlled by settings
- [x] Lifecycle startup/shutdown logging
- [ ] Request correlation IDs (deferred to a later phase)

## Phase 1.4

- [x] Add `dependency-injector` dependency
- [x] Application container (`app/container.py`)
- [x] Settings and logger providers
- [x] Container wired into the application factory
- [x] Container exposed on `app.state.container`
- [x] FastAPI dependencies (`app/dependencies.py`)
- [x] README documentation for dependency injection

## Phase 1.5

- [x] Base `TWIBException` (`app/core/exceptions.py`)
- [x] Generic exception hierarchy
- [x] Error code registry (`app/core/error_codes.py`)
- [x] Global exception handlers (`app/core/handlers.py`)
- [x] Handlers registered in the application factory
- [x] Consistent JSON error responses
- [x] No tracebacks exposed to clients
- [x] README documentation for error handling

## Phase 1.6

- [x] Middleware package (`app/middleware/`)
- [x] Request ID middleware (UUID4, `request.state.request_id`, header)
- [x] Security headers middleware
- [x] Settings-driven CORS
- [x] Central `register_middlewares()` registration
- [x] Application factory calls `register_middlewares()` only
- [x] README documentation for middleware

## Phase 1.7

- [x] Reusable response models (`app/schemas/response.py`)
- [x] Generic `SuccessResponse[T]`
- [x] Reusable pagination schemas (`app/schemas/pagination.py`)
- [x] Reusable common schemas (`app/schemas/common.py`)
- [x] Centralized API tags (`app/api/tags.py`)
- [x] OpenAPI metadata module (`app/api/openapi.py`)
- [x] OpenAPI wired into the application factory
- [x] Centralized response helpers (`app/api/responses.py`)
- [x] Error handlers reuse the `ErrorResponse` schema
- [x] README documentation for the API foundation

## Phase 1.8

- [x] Configure Ruff (lint, format, import sorting, Python 3.12)
- [x] Configure MyPy strict typing
- [x] Centralize code quality configuration in `pyproject.toml`
- [x] Create `.pre-commit-config.yaml` (Ruff lint, Ruff format, MyPy)
- [x] Add `ruff`, `mypy`, `pre-commit`, `types-requests` dev dependencies
- [x] README documentation for code quality

## Phase 1.9

- [x] Add `pytest`, `pytest-asyncio`, `pytest-cov`, `httpx` dev dependencies
- [x] Configure test discovery, coverage, and async support in `pytest.ini`
- [x] Create `backend/tests/` package (`__init__.py`, `conftest.py`, `test_health.py`)
- [x] Reusable TestClient fixture (`client` in `conftest.py`)
- [x] Health endpoint tests (status code, response model, application starts, content type)
- [x] README documentation for testing

## Phase 1.10

- [x] Development Dockerfile (Python 3.12, uv, non-root user, port 8000, hot reload)
- [x] Root `.dockerignore` (backend-only build context)
- [x] `docker/development/docker-compose.yml`
- [x] Backend service (reads `.env`, source bind mount, health check)
- [x] Supporting services (postgres, redis, qdrant) with named volumes
- [x] Single development bridge network
- [x] README documentation for Docker

## Phase 1.11

- [x] `RequestContext` object (`app/observability/request_context.py`)
- [x] Event definitions (`app/observability/events.py`)
- [x] Metrics interfaces (`app/observability/metrics.py`)
- [x] Tracing interfaces (`app/observability/tracing.py`)
- [x] `ObservabilityMiddleware` (`app/middleware/observability.py`)
- [x] Middleware registered in the application stack
- [x] README documentation for observability

## Phase 1.12

- [x] Multi-stage production Dockerfile
- [x] Production Docker Compose
- [x] Docker image optimization
- [x] Production health checks
- [x] README documentation for production Docker

## Phase 1.13

- [x] Foundation review
- [x] ADR-0008 backend package layout
- [x] ADR-0009 authentication (hybrid) decision
- [x] Sync folder_structure.md / coding_guidelines.md / development_workflow.md

## Phase 2.1

- [x] Domain package (`backend/app/domain/`)
- [x] `Identity[T]` value type
- [x] `Entity` base class
- [x] `AggregateRoot` base class
- [x] `ValueObject` base class
- [x] `DomainEvent` base class
- [x] Domain exception hierarchy
- [x] Framework-independent (pure Python, no FastAPI/Pydantic/SQLAlchemy)
- [x] README documentation for the domain layer

## Phase 2.2

- [x] Value objects package (`backend/app/domain/value_objects/`)
- [x] `UuidIdentity` (generate/parse)
- [x] `Email`
- [x] `Name`
- [x] `Slug`
- [x] `Timestamp` (now/parse)
- [x] `Url`
- [x] `Version` (parse)
- [x] `Money`
- [x] `Metadata`
- [x] `InvalidValue` exception added to the domain hierarchy
- [x] Immutable, self-validating, value-comparable, meaningful string repr
- [x] Pure Python (no dataclasses, FastAPI, Pydantic, SQLAlchemy)
- [x] README documentation for the concrete value objects

## Phase 2.3

- [x] User domain package (`backend/app/domain/users/`)
- [x] `User` aggregate root built from the Phase 2.2 value objects
- [x] `UserStatus` enum (pending, active, suspended, disabled, deleted)
- [x] `UserRole` enum (owner, admin, member, viewer)
- [x] User domain events (created, activated, suspended, deleted, email/name changed)
- [x] User business-rule exceptions
- [x] Domain methods with validation, event recording, and version bumping
- [x] Read-only property exposure (no mutable attributes)
- [x] Pure Python (no FastAPI, Pydantic, SQLAlchemy, repositories, auth)
- [x] README documentation for the user aggregate

## Phase 2.4

- [x] Organization domain package (`backend/app/domain/organizations/`)
- [x] Organization aggregate root
- [x] Memberships and organization roles
- [x] Organization domain events and invariants
- [x] README documentation for the organization domain

## Phase 2.5

- [x] Workspace domain package (`backend/app/domain/workspaces/`)
- [x] Workspace aggregate root
- [x] Workspace membership and roles
- [x] Workspace settings domain object
- [x] Workspace domain events and invariants
- [x] `Description` value object
- [x] README documentation for the workspace domain

## Phase 2.6

- [ ] Repository interfaces package (`backend/app/domain/repositories/`)
- [ ] `UserRepository` protocol
- [ ] `OrganizationRepository` protocol
- [ ] `WorkspaceRepository` protocol
- [ ] README documentation for the repository interfaces

---

# Known Issues

None

---

# Technical Debt

None

---

# Open Decisions

None

Architecture is locked.

---

# Blockers

None

---

# Development Rules

Every AI model must read before generating code:

1. architecture.md
2. PROJECT_RULES.md
3. AI_SPECIFICATION.md
4. PROJECT_STATUS.md

---

# Session Notes

Session 1

Completed

- Enterprise documentation
- AI architecture
- Rules
- Specifications

Session 2

Completed

- Phase 1.1 FastAPI bootstrap

Session 3

Completed

- Phase 1.2 Configuration System

Session 4

Completed

- Phase 1.3 Structured Logging

Session 5

Completed

- Phase 1.4 Dependency Injection

Session 6

Completed

- Phase 1.5 Exception Handling

Session 7

Completed

- Phase 1.6 Middleware

Session 8

Completed

- Phase 1.7 API Foundation

Session 9

Completed

- Phase 1.8 Code Quality

Session 10

Completed

- Phase 1.9 Testing Infrastructure

Session 11

Completed

- Phase 1.10 Docker Development Environment

Session 12

Completed

- Phase 1.11 Observability Foundation

Session 13

Completed

- Phase 1.12 Docker Production

Session 14

Completed

- Phase 1.13 Foundation Review (audit, ADR-0008, ADR-0009, doc sync)

Session 15

Completed

- Phase 2.1 Domain Foundation (entities, aggregates, value objects, domain
  events, identities, domain exceptions)

Session 16

Completed

- Phase 2.2 Value Objects (UUID identity, email, name, slug, timestamp, URL,
  version, money, metadata)

Session 17

Completed

- Phase 2.3 User Domain (User aggregate root, user statuses, roles, domain
  events, business-rule exceptions)

Session 18

Completed

- Phase 2.4 Organization Domain (Organization aggregate root, immutable
  memberships, subscription plans, organization statuses, domain events,
  business-rule exceptions)

Session 19

Completed

- Phase 2.5 Workspace Domain (Workspace aggregate root, immutable
  memberships and settings, workspace roles and statuses, domain events,
  business-rule exceptions, Description value object)

Next Session

Phase 2.6

Repository Interfaces

---

# Phase 1.12 Summary

## Files Created

- docker/production/docker-compose.yml

## Files Modified

- Dockerfile
- backend/README.md
- docs/PROJECT_STATUS.md

## Architectural Decisions

- The single root `Dockerfile` is now multi-stage. `runtime` is the minimal
  production image and `development` is the default (last) stage, so the
  unchanged development Compose stack (`docker compose build`, no target)
  still produces the development image while the production stack builds
  `target: runtime`.
- The `runtime` stage installs only the locked runtime dependencies
  (`uv sync --frozen --no-dev`) and copies only the compiled virtual
  environment and the application source; the `uv` CLI, manifest files, and
  dev dependencies are not present in the final image.
- The image runs as the non-root `twib` user (uid/gid 1000) and registers a
  Docker `HEALTHCHECK` against `/api/v1/health` using the standard library
  `urllib` (no extra binaries in the image).
- `docker/production/docker-compose.yml` mirrors the development services
  but uses a dedicated `twib-prod` network and project name, `build.target:
  runtime`, `APP_ENV=production` (forced), named volumes, `restart:
  unless-stopped` on every service, health-check-gated `depends_on`, and
  no bind mounts or hot reload.
- Only the backend publishes a host port (`8000:8000`); supporting-service
  ports are not exposed on the host in production.
- No Kubernetes, Helm, Terraform, GitHub Actions, NGINX, Traefik, cloud
  deployment, monitoring, observability, or application changes were made.

## Suggestions (Not Implemented)

- Docker could not be executed during this phase (per the phase rules), so
  the image build and `docker compose up` were not verified at runtime.
  Run `docker compose -f docker/production/docker-compose.yml config`,
  `docker build --target runtime -t twib-backend:production ../..`, and
  `docker compose up` after this phase to confirm the production stack
  starts and the health checks pass.
- The production image runs a single uvicorn worker. Add `--workers` (or
  compose replicas) once the workload requires it.
- The uv image is pinned to `ghcr.io/astral-sh/uv:latest` in both build
  chains. Pin a specific uv release for fully reproducible builds.
- The `development` stage still uses `uv sync --all-groups` (not
  `--frozen`). Switch it to `--frozen` once the lockfile is verified fresh.
- Supporting-service image tags (postgres 17, redis 7, qdrant v1.14.0)
  should be reviewed when the database and cache phases land.
- No reverse proxy (NGINX/Traefik), orchestration, or cloud deployment is
  included; those remain out of scope for the foundation phases.
- No application source files were modified in this phase.

---

# Phase 1.13 Summary

## Files Created

- docs/adr/0008-backend-package-layout.md
- docs/adr/0009-authentication-hybrid.md

## Files Modified

- docs/folder_structure.md
- docs/coding_guidelines.md
- docs/development_workflow.md
- docs/INDEX.md
- docs/architecture.md
- docs/PROJECT_STATUS.md

## Architectural Decisions

- ADR-0008: the backend is a single `backend/app/` package imported as
  `app.*`. The README-only scaffolding directories directly under `backend/`
  (api, config, dependencies, exceptions, middleware, schemas, services,
  utils, websocket) are deprecated and must not receive new code.
- ADR-0009: authentication is hybrid. Auth0/Clerk acts as the managed
  Identity Provider (login, SSO, MFA); TWIB mints its own short-lived
  session JWTs signed with `SECRET_KEY` plus opaque refresh tokens in Redis.
  RBAC and API keys are TWIB-owned. `SECRET_KEY` becomes mandatory in
  production.

## Summary

- Completed the Phase 1.13 read-only foundation audit (docs vs
  implementation, folder structure, code quality, security, Docker) and
  produced the full audit report (score 9/10, PASS WITH MINOR ISSUES).
- Drafted ADR-0008 and ADR-0009 to close the two audit MUST-Fix items.
- Synced `folder_structure.md`, `coding_guidelines.md`, and
  `development_workflow.md` to the implemented `app/` layout, the uv
  toolchain, and the real Docker compose paths and uvicorn entrypoint.
- No application source, tests, or Docker files were changed in this phase.

## Suggestions (Not Implemented)

- The deprecated `backend/` scaffolding README directories are still on disk;
  Phase 2 cleanup should remove them (see ADR-0008).
- Audit Nice-to-Have items remain open: health route still returns a plain
  dict, validation-error details still include `input`, `SECRET_KEY` is not
  enforced in production, uv is pinned to `latest`, dev uses non-frozen sync,
  no coverage fail-under, and Makefile/scripts/.github do not exist yet.
- `roadmap.md` Phase 1 status and the roadmap/TECH_STACK authentication
  wording can be aligned to ADR-0009 when the roadmap is next updated.

---

# Phase 2.1 Summary

## Files Created

- backend/app/domain/__init__.py
- backend/app/domain/base.py
- backend/app/domain/entity.py
- backend/app/domain/aggregate.py
- backend/app/domain/value_object.py
- backend/app/domain/event.py
- backend/app/domain/exceptions.py

## Files Modified

- backend/README.md
- docs/PROJECT_STATUS.md

## Dependencies Added

None

## Verification Results

- `Identity[T]` is an immutable value wrapper around an entity identifier
  (UUID, string, or integer); it is compared and hashed by value, cannot be
  mutated after construction, and renders as the wrapped value.
- `Entity` compares and hashes by type and identity, so two entities with the
  same identity are equal regardless of their state; a runtime smoke test
  confirmed identity-based equality, hashing, and entity-state mutation.
- `AggregateRoot` records `DomainEvent` instances through `record_event()` and
  returns them exactly once through `pull_domain_events()`; the smoke test
  confirmed events are returned in order and the record clears.
- `ValueObject` provides value-based equality, hashing, and representation;
  frozen dataclass subclasses inherit them (`@dataclass(frozen=True, eq=False)`).
- `DomainEvent` uses keyword-only `event_id` (UUID4) and `occurred_at` (UTC)
  defaults plus a derived `event_name`; concrete events add payload fields
  without defaults.
- Domain exceptions (`DomainException`, `BusinessRuleViolation`,
  `EntityNotFound`, `InvalidOperation`) form a framework-independent hierarchy
  carrying `message` and optional `details`.
- `ruff check` and `ruff format --check` pass across `backend/app/domain`.
- `mypy --strict` passes across `backend/app/domain`.
- A runtime smoke test (imports, identity immutability, entity equality,
  aggregate event recording, value-object equality, domain-event construction,
  exception hierarchy) succeeds.
- No authentication, database, repository, FastAPI route, Pydantic model, ORM,
  or external dependency was added.

## Architectural Decisions

- The domain layer lives in `backend/app/domain/` per ADR-0008 (new modules
  are subpackages of `app/`). The canonical base classes are defined in their
  concept modules (`entity.py`, `aggregate.py`, `value_object.py`, `event.py`);
  `base.py` aggregates them as a single import surface and `__init__.py`
  exports the public domain API.
- The domain layer is pure Python: it imports only the standard library. It
  does not reuse `app.core.exceptions` (which is FastAPI-aware) but defines
  its own exception hierarchy; outer layers translate domain exceptions into
  the HTTP-aware `TWIBException` contract.
- Classes follow the Phase 1.8 PEP 695 type-parameter convention
  (`Entity[EntityID: uuid.UUID | str | int]`); constructor parameters that
  would shadow the `id` builtin are named `id_`.
- `DomainEvent` base fields are keyword-only so concrete event subclasses can
  declare required payload fields without defaults (no dataclass field-order
  error).

## Suggestions (Not Implemented)

- `folder_structure.md` still lists `app/models/` as the future home of
  domain models; the implemented home is `app/domain/`. ADR-0008 permits new
  subpackages under `app/`, so no ADR was required, but the docs can be
  aligned when the roadmap is next updated.
- No unit tests were added in this phase (the phase scope was the domain
  foundation only, and running the test tooling was out of scope). Phase 2.2
  should add `backend/tests/domain/` unit tests for the base classes.
- `ValueObject` and `Entity` are not ABCs (they declare no abstract methods),
  so they can be instantiated directly; this keeps ruff B024 clean and follows
  the existing config-level exemptions. Subclasses supply the identity or
  payload.

---

# Phase 2.3 Summary

## Files Created

- backend/app/domain/users/__init__.py
- backend/app/domain/users/user.py
- backend/app/domain/users/role.py
- backend/app/domain/users/status.py
- backend/app/domain/users/events.py
- backend/app/domain/users/exceptions.py

## Files Modified

- backend/README.md
- docs/PROJECT_STATUS.md

## Dependencies Added

None

## Verification Results

- `User` extends `AggregateRoot[uuid.UUID]` and is built entirely from the
  Phase 2.2 value objects (`UuidIdentity`, `Email`, `Name`, `Timestamp`,
  `Metadata`, `Version`) plus the `UserStatus`/`UserRole` enums; state is
  exposed only through read-only properties.
- Construction records a `UserCreated` event; `pull_domain_events()` returns
  events in order and clears the record.
- `change_display_name()` and `change_email()` validate, record
  `UserNameChanged`/`UserEmailChanged` (carrying new and previous values), and
  are no-ops when the value is unchanged.
- `change_email()` raises `EmailAlreadyAssigned` when the new email equals the
  email already assigned to the user.
- `activate()` raises `UserAlreadyActive` when already active; `deactivate()`,
  `suspend()`, `restore()`, and `delete()` enforce their state transitions and
  raise `InvalidUserState` on invalid ones.
- `suspend()` raises `CannotSuspendOwner` for users with the OWNER role.
- `delete()` is terminal: every later mutation raises `InvalidUserState`.
- Every successful mutation refreshes `updated_at` and bumps `version` by one
  patch; `increment_version()` exposes an explicit bump.
- `metadata` returns the immutable `Metadata` value object (a copy of the
  internal map), so it cannot be mutated externally.
- `User` equality and hashing follow the `Entity` contract (same type and
  identity), so two aggregates wrapping the same UUID are equal.
- `UserStatus` and `UserRole` are `StrEnum`s with the documented members.
- `ruff check` and `ruff format --check` pass across `backend/app/domain`.
- `mypy --strict` passes across `backend/app/domain`.
- A runtime smoke test (creation, read-only properties, every domain method,
  each event, every exception path, version bumping, and identity equality)
  succeeds.
- No authentication, password hashing, JWT, database model, repository, API
  route, or external dependency was added.

## Architectural Decisions

- `User` subclasses `AggregateRoot[uuid.UUID]` and bridges to the base's
  identity contract with the generic `Identity(user_id.value)`; the canonical
  identifier exposed to callers is the `UuidIdentity` value object via the
  `user_id` property. This reuses the Phase 2.1 aggregate machinery (event
  recording, identity equality) without modifying the Phase 2.2 identity.
- The aggregate's state lives in private fields and is exposed only through
  read-only properties; mutability happens exclusively through domain methods
  that enforce business rules, so no mutable attribute is exposed directly.
- Optimistic locking is modelled as an auto-bumping `Version`: every
  successful domain method calls `_touch()` (refresh `updated_at`, bump the
  version), and `increment_version()` is provided for explicit out-of-band
  bumps.
- `UserStatus` and `UserRole` are `StrEnum`s (per the Phase 1.8 UP042
  convention and the coding guidelines enum pattern) rather than value-object
  wrappers; they are immutable and string-comparable by construction.
- User domain exceptions subclass `BusinessRuleViolation` (a
  `DomainException`), matching their semantics as enterprise business-rule
  violations and keeping them framework-independent.
- User events subclass `DomainEvent` and carry the affected `user_id` plus the
  new and previous values for the change events, so consumers have everything
  they need without querying state.

## Suggestions (Not Implemented)

- No unit tests were added in this phase (running the pytest tooling is out of
  scope per the phase rules). Phase 2.4 should add `backend/tests/domain/`
  unit tests covering the value objects and the user aggregate.
- `deactivate()` and `restore()` do not emit domain events (the phase
  specified exactly six events). A future phase can add `UserDeactivated` and
  `UserRestored` events for full auditability.
- `EmailAlreadyAssigned` is currently raised only when the new email equals
  the email already assigned to this user. Cross-user duplicate detection
  requires the repository/application service and will land with the database
  phase.
- `update_metadata()` replaces the whole metadata map rather than merging.
  Per-key merge/removal APIs can be added once persistence exists.
- No permissions are modelled for `UserRole`; a future RBAC phase will attach
  permissions to roles.
- The `User` constructor accepts optional `created_at`, `updated_at`,
  `status`, `role`, `metadata`, and `version` so outer layers can reconstruct
  aggregates from storage; there is no persistence code yet.
- `folder_structure.md` still lists `app/models/` as the future home of
  domain models; the implemented home is `app/domain/`. The docs can be
  aligned when the roadmap is next updated.

---

# Phase 2.4 Summary

## Files Created

- backend/app/domain/organizations/__init__.py
- backend/app/domain/organizations/organization.py
- backend/app/domain/organizations/membership.py
- backend/app/domain/organizations/plan.py
- backend/app/domain/organizations/status.py
- backend/app/domain/organizations/events.py
- backend/app/domain/organizations/exceptions.py

## Files Modified

- backend/README.md
- docs/PROJECT_STATUS.md

## Dependencies Added

None

## Verification Results

- `Organization` extends `AggregateRoot[uuid.UUID]` and is built entirely
  from the Phase 2.2 value objects (`UuidIdentity`, `Name`, `Slug`,
  `Timestamp`, `Metadata`, `Version`) plus the `OrganizationStatus` and
  `SubscriptionPlan` enums; state is exposed only through read-only
  properties.
- Construction implicitly adds the owner as an active OWNER-role member and
  records an `OrganizationCreated` event; `pull_domain_events()` returns
  events in order and clears the record.
- `rename()`, `change_slug()`, `change_plan()`, and `update_metadata()` are
  no-ops when the new value equals the current one.
- `activate()` raises `InvalidOrganizationState` when already active;
  `suspend()` behaves likewise; `archive()` raises `OrganizationArchived`
  when already archived; `restore()` raises `InvalidOrganizationState` when
  not archived.
- An archived organization is immutable: every later mutation raises
  `OrganizationArchived` until `restore()`.
- `add_member()` raises `DuplicateMember` for an existing active member and
  `MembershipAlreadyExists` for an existing pending membership.
- `remove_member()` raises `OwnerCannotBeRemoved` for the owner and
  `InvalidOrganizationState` for a non-member.
- `change_owner()` only accepts an existing member (else
  `InvalidOrganizationState`), records `OwnerChanged` with new and previous
  owner IDs, and swaps roles (new owner becomes OWNER, previous owner
  becomes ADMIN).
- `OrganizationMembership` is immutable (raises `TypeError` on assignment)
  and its constructor rejects an accepted invitation in the PENDING state
  and a non-pending membership without an accepted invitation
  (`InvalidValue`); memberships compare and hash by value.
- Every successful mutation refreshes `updated_at` and bumps `version` by
  one patch; `increment_version()` exposes an explicit bump.
- `OrganizationStatus` and `SubscriptionPlan` are `StrEnum`s with the
  documented members; `MembershipStatus` covers pending, active, and
  inactive.
- `ruff check` and `ruff format --check` pass across `backend/app/domain`.
- `mypy --strict` passes across `backend/app/domain`.
- A runtime smoke test (creation, owner auto-membership, every domain
  method, each event, every exception path, and version bumping) succeeds.
- No authentication, billing, plan-limit, database model, repository, API
  route, or external dependency was added.

## Architectural Decisions

- `Organization` subclasses `AggregateRoot[uuid.UUID]` and bridges to the
  base's identity contract with the generic `Identity(organization_id.value)`;
  the canonical identifier exposed to callers is the `UuidIdentity` value
  object via the `organization_id` property (same pattern as `User`).
- The aggregate's state lives in private fields and is exposed only through
  read-only properties; mutability happens exclusively through domain
  methods that enforce business rules, so no mutable attribute is exposed
  directly.
- The owner is an implicit, always-present active OWNER-role member. The
  owner cannot be removed (`OwnerCannotBeRemoved`); ownership transfers via
  `change_owner()` which swaps roles so the organization always retains
  exactly one owner.
- Memberships are immutable domain objects stored privately in a
  `dict[UuidIdentity, OrganizationMembership]` and exposed as a tuple;
  `get_member()` provides lookup. Membership is a domain object only, not
  an aggregate.
- Optimistic locking mirrors the user aggregate: every successful domain
  method calls `_touch()` (refresh `updated_at`, bump the version), and
  `increment_version()` is provided for explicit out-of-band bumps.
- `OrganizationStatus` and `SubscriptionPlan` are `StrEnum`s (per the
  Phase 1.8 UP042 convention) rather than value-object wrappers; plan
  limits and billing are intentionally out of scope.
- Organization domain exceptions subclass `BusinessRuleViolation`, matching
  their semantics as enterprise business-rule violations.
- Organization events subclass `DomainEvent` and carry the affected
  `organization_id` plus new and previous values for the change events
  (`OrganizationRenamed`, `OwnerChanged`, `PlanChanged`), so consumers have
  everything they need without querying state.

## Suggestions (Not Implemented)

- No unit tests were added in this phase (running the pytest tooling is out
  of scope per the phase rules). A future phase should add
  `backend/tests/domain/` unit tests covering the value objects, the user
  aggregate, and the organization aggregate.
- `archive()`, `restore()`, `change_slug()`, `change_owner()` (via
  `change_owner`), and membership role changes do not emit domain events
  (the phase specified exactly eight events). A future phase can add
  `OrganizationArchived`, `OrganizationRestored`, `SlugChanged`, and
  `MemberRoleChanged` events for full auditability.
- `add_member()` only creates ACTIVE members. Invitation flows (creating
  PENDING memberships and later accepting them) require an application
  service and will land with the database phase; the `MembershipStatus`
  enum and constructor validation already support pending memberships.
- Membership removal is immediate (`remove_member()` deletes the
  membership). A soft-delete or `INACTIVE`-transition flow can be added
  once persistence exists.
- `change_plan()` only records the plan change; no plan limits,
  entitlements, or downgrade checks are modelled. Billing logic belongs to
  a future billing phase.
- The `Organization` constructor accepts optional `created_at`, `updated_at`,
  `status`, `subscription_plan`, `metadata`, and `version` so outer layers
  can reconstruct aggregates from storage; there is no persistence code yet.
- `folder_structure.md` still lists `app/models/` as the future home of
  domain models; the implemented home is `app/domain/`. The docs can be
  aligned when the roadmap is next updated.

---

# Phase 2.5 Summary

## Files Created

- backend/app/domain/value_objects/description.py
- backend/app/domain/workspaces/__init__.py
- backend/app/domain/workspaces/workspace.py
- backend/app/domain/workspaces/membership.py
- backend/app/domain/workspaces/settings.py
- backend/app/domain/workspaces/status.py
- backend/app/domain/workspaces/events.py
- backend/app/domain/workspaces/exceptions.py

## Files Modified

- backend/app/domain/value_objects/__init__.py (exported `Description`)
- backend/README.md
- docs/PROJECT_STATUS.md

## Dependencies Added

None

## Verification Results

- `Workspace` extends `AggregateRoot[uuid.UUID]` and is built entirely from
  the Phase 2.2 value objects (`UuidIdentity`, `Name`, `Slug`,
  `Description`, `Timestamp`, `Metadata`, `Version`), the `WorkspaceStatus`
  enum, and the `WorkspaceSettings` domain object; state is exposed only
  through read-only properties.
- Construction implicitly adds the owner as an active OWNER-role member and
  records a `WorkspaceCreated` event carrying the parent organization ID;
  `pull_domain_events()` returns events in order and clears the record.
- `rename()`, `change_slug()`, `change_description()`, `update_settings()`,
  and `update_metadata()` are no-ops when the new value equals the current
  one.
- `activate()` raises `InvalidWorkspaceState` when already active; a
  suspended workspace becomes active. `suspend()` raises
  `InvalidWorkspaceState` when already suspended.
- `archive()` raises `WorkspaceArchived` when already archived and records a
  `WorkspaceArchived` event; `restore()` raises `InvalidWorkspaceState` when
  not archived.
- An archived workspace is immutable: every later mutation raises
  `WorkspaceArchived` until `restore()`.
- `add_member()` raises `DuplicateWorkspaceMember` for an existing member;
  `remove_member()` raises `OwnerCannotBeRemoved` for the owner and
  `InvalidWorkspaceState` for a non-member.
- `change_owner()` only accepts an existing member (else
  `InvalidWorkspaceState`), records `WorkspaceOwnerChanged` with new and
  previous owner IDs, and swaps roles (new owner becomes OWNER, previous
  owner becomes ADMIN).
- `WorkspaceMembership` is immutable (raises `TypeError` on assignment) and
  its constructor rejects an accepted invitation in the PENDING state and a
  non-pending membership without an accepted invitation (`InvalidValue`);
  memberships compare and hash by value.
- `WorkspaceSettings` is immutable (raises `TypeError` on assignment),
  validates non-empty strings and a non-negative execution limit
  (`InvalidValue`), and compares and hashes by value.
- Every successful mutation refreshes `updated_at` and bumps `version` by
  one patch; `increment_version()` exposes an explicit bump.
- `WorkspaceStatus`, `WorkspaceRole`, `WorkspaceMembershipStatus`, and
  `WorkspaceVisibility` are `StrEnum`s with the documented members.
- `Description` trims the value, allows an empty description, and enforces a
  500-character maximum length.
- `ruff check` and `ruff format --check` pass across `backend/app/domain`.
- `mypy --strict` passes across `backend/app/domain`.
- A runtime smoke test (creation, owner auto-membership, every domain
  method, each event, every exception path, and version bumping) succeeds.
- No authentication, billing, plan-limit, database model, repository, API
  route, or external dependency was added.

## Architectural Decisions

- `Workspace` subclasses `AggregateRoot[uuid.UUID]` and bridges to the base's
  identity contract with the generic `Identity(workspace_id.value)`;
  the canonical identifier exposed to callers is the `UuidIdentity` value
  object via the `workspace_id` property (same pattern as `User` and
  `Organization`).
- The aggregate's state lives in private fields and is exposed only through
  read-only properties; mutability happens exclusively through domain methods
  that enforce business rules, so no mutable attribute is exposed directly.
- The owner is an implicit, always-present active OWNER-role member. The
  owner cannot be removed (`OwnerCannotBeRemoved`); ownership transfers via
  `change_owner()` which swaps roles so the workspace always retains exactly
  one owner.
- Memberships are immutable domain objects stored privately in a
  `dict[UuidIdentity, WorkspaceMembership]` and exposed as a tuple;
  `get_member()` provides lookup. Membership is a domain object only, not an
  aggregate.
- Workspace configuration is an immutable `WorkspaceSettings` domain object
  (not a value object per field), so the whole configuration can be replaced
  atomically through `update_settings()` and compared by value.
- Optimistic locking mirrors the user and organization aggregates: every
  successful domain method calls `_touch()` (refresh `updated_at`, bump the
  version), and `increment_version()` is provided for explicit out-of-band
  bumps.
- `WorkspaceStatus`, `WorkspaceRole`, `WorkspaceMembershipStatus`, and
  `WorkspaceVisibility` are `StrEnum`s (per the Phase 1.8 UP042 convention);
  workspace permissions are intentionally out of scope.
- `Description` is a Phase 2.2-style value object added to
  `app/domain/value_objects/` so it is reusable by later aggregates (for
  example workflows and projects).
- Workspace domain exceptions subclass `BusinessRuleViolation`, matching
  their semantics as enterprise business-rule violations.
- Workspace events subclass `DomainEvent` and carry the affected
  `workspace_id` plus new and previous values for the change events
  (`WorkspaceRenamed`, `WorkspaceOwnerChanged`, `WorkspaceSettingsChanged`),
  so consumers have everything they need without querying state.
- `WorkspaceArchived` names both a domain event and a business-rule
  exception. The package-level export is the exception; the event is imported
  from `app.domain.workspaces.events` to avoid the name collision.

## Suggestions (Not Implemented)

- No unit tests were added in this phase (running the pytest tooling is out
  of scope per the phase rules). A future phase should add
  `backend/tests/domain/` unit tests covering the value objects and the user,
  organization, and workspace aggregates.
- `change_slug()`, `change_description()`, `activate()`, `suspend()`, and
  `restore()` do not emit domain events (the phase specified exactly seven
  events). A future phase can add `WorkspaceSlugChanged`,
  `WorkspaceActivated`, `WorkspaceSuspended`, and `WorkspaceRestored` events
  for full auditability.
- `WorkspaceAlreadyExists` is defined but is not raised by the aggregate
  itself; detecting a duplicate workspace (for example a shared slug)
  requires the application/repository layer and will land with the database
  phase.
- `add_member()` only creates ACTIVE members. Invitation flows (creating
  PENDING memberships and later accepting them) require an application
  service and will land with the database phase; the `WorkspaceRole` and
  `WorkspaceMembershipStatus` enums already support pending memberships.
- Membership removal is immediate (`remove_member()` deletes the
  membership). A soft-delete or `INACTIVE`-transition flow can be added once
  persistence exists.
- `WorkspaceSettings` stores primitives (timezone, language, visibility,
  model preference, limits, toggles). No plan limits, entitlements, or
  per-plan settings validation is modelled; billing logic belongs to a future
  billing phase.
- The `Workspace` constructor accepts optional `created_at`, `updated_at`,
  `status`, `settings`, `metadata`, and `version` so outer layers can
  reconstruct aggregates from storage; there is no persistence code yet.
- `folder_structure.md` still lists `app/models/` as the future home of
  domain models; the implemented home is `app/domain/`. The docs can be
  aligned when the roadmap is next updated.

---

# Phase 2.2 Summary

## Files Created

- backend/app/domain/value_objects/__init__.py
- backend/app/domain/value_objects/id.py
- backend/app/domain/value_objects/email.py
- backend/app/domain/value_objects/name.py
- backend/app/domain/value_objects/slug.py
- backend/app/domain/value_objects/timestamp.py
- backend/app/domain/value_objects/url.py
- backend/app/domain/value_objects/version.py
- backend/app/domain/value_objects/money.py
- backend/app/domain/value_objects/metadata.py

## Files Modified

- backend/app/domain/exceptions.py (added `InvalidValue`)
- backend/app/domain/__init__.py (exported `InvalidValue`)
- backend/README.md
- docs/PROJECT_STATUS.md

## Dependencies Added

None

## Verification Results

- `UuidIdentity` wraps a UUID4, generates a fresh identity with `generate()`,
  parses the canonical string form with `parse()`, compares and hashes by
  value, and is immutable; invalid UUID strings raise `InvalidValue`.
- `Email` normalizes to lowercase and trims surrounding whitespace; empty and
  malformed addresses raise `InvalidValue`; equality and hashing are by value.
- `Name` trims the value, rejects empty names, and enforces a 120-character
  maximum length.
- `Slug` normalizes to lowercase and enforces the strict `a-z0-9` plus single
  hyphen pattern (no leading/trailing/repeated hyphens, no spaces).
- `Timestamp` requires a timezone-aware moment, normalizes to UTC, and offers
  `now()` and `parse()` (ISO 8601); naive moments raise `InvalidValue`.
- `Url` accepts only absolute `http`/`https` URLs with a host; unsupported
  schemes and missing hosts raise `InvalidValue`.
- `Version` stores non-negative `major.minor.patch` components and parses the
  dotted string form; negative components and malformed strings raise
  `InvalidValue`.
- `Money` stores a `Decimal` amount (int/str parsed with `Decimal`) and a
  normalized ISO 4217 currency code (three uppercase letters); unparseable
  amounts and invalid currencies raise `InvalidValue`.
- `Metadata` stores an immutable string key/value map; the mapping is copied
  at construction and `value` returns a fresh copy, so the stored data can
  never be mutated from outside.
- All value objects raise `InvalidValue` (a `DomainException` subclass) on
  invalid input, block mutation after construction, and compare and hash by
  value.
- `ruff check` and `ruff format --check` pass across `backend/app/domain`.
- `mypy --strict` passes across `backend/app/domain`.
- A runtime smoke test (generation, parsing, normalization, validation,
  equality, hashing, immutability, and `InvalidValue` behaviour for all nine
  value objects) succeeds.
- No authentication, database, repository, FastAPI route, Pydantic model,
  ORM, or external dependency was added.

## Architectural Decisions

- Concrete value objects live in `backend/app/domain/value_objects/` as a
  subpackage of the domain layer (per ADR-0008) and are imported from
  `app.domain.value_objects`. `app/domain/__init__.py` keeps exporting only
  the base classes and exceptions; value objects are imported from their own
  package to keep the public domain surface focused.
- The concrete value objects do not use dataclasses (unlike the `ValueObject`
  base-class pattern documented in Phase 2.1). Immutability is enforced by
  overriding `__setattr__` to reject assignments after construction, and
  instance attributes are declared with annotations so `mypy --strict` can
  verify them.
- Scalar value objects subclass the Phase 2.1 `ValueObject` base class, which
  supplies value-based equality, hashing, and representation. `UuidIdentity`
  is a standalone value type (modelled on the generic `Identity` in
  `entity.py`) so it does not compare equal to a generic `Identity` wrapping
  the same UUID.
- Value objects accept and normalize `str` input (`parse`/class methods), so
  outer layers can safely reconstruct them from storage and requests without
  an ORM.
- The domain exception hierarchy gained `InvalidValue`, the dedicated
  exception for malformed value-object input; the Phase 2.1 exceptions remain
  unchanged.

## Suggestions (Not Implemented)

- No unit tests were added in this phase (running the pytest tooling is out
  of scope per the phase rules). Phase 2.3 should add
  `backend/tests/domain/` unit tests covering the value objects and the user
  entity.
- `Version` has no ordering operators (`<`, `<=`, `>`, `>=`). They are
  semantically meaningful for versions but were left out to keep the phase
  focused on value semantics and validation; add them when version ordering
  is actually needed.
- `Money` has no arithmetic operators or currency conversion (no `__add__`,
  `__mul__`, or exchange-rate logic). These are domain operations that belong
  to a billing phase, not to the value object itself.
- `Metadata` values are restricted to strings for hashability and simplicity;
  the Phase 1.7 `app/schemas/common.py` `Metadata` alias is still
  `dict[str, Any]` and remains the serialization-side concern.
- `Email` validation is a pragmatic regular expression; it accepts most valid
  addresses and rejects clearly malformed ones but does not implement the full
  RFC 5322 grammar. Tighten it if a stricter contract is ever needed.
- `Url` validates scheme and host presence but performs no network-level or
  DNS checks, which is intentional for a domain value object.
- `folder_structure.md` still lists `app/models/` as the future home of
  domain models; the implemented home is `app/domain/`. The docs can be
  aligned when the roadmap is next updated.

---

# Phase 1.11 Summary

## Files Created

- backend/app/observability/__init__.py
- backend/app/observability/request_context.py
- backend/app/observability/events.py
- backend/app/observability/metrics.py
- backend/app/observability/tracing.py
- backend/app/middleware/observability.py

## Files Modified

- backend/app/middleware/registration.py
- backend/app/middleware/__init__.py
- backend/README.md
- docs/PROJECT_STATUS.md

## Dependencies Added

None

## Verification Results

- `RequestContext` is a Pydantic model with `request_id`, `timestamp`, and
  `correlation_id` required and `trace_id`, `user_id`, and
  `organization_id` defaulting to `None`; `model_dump()` reports the
  optional fields as `None`.
- `app/observability/events.py` defines the five `EventType` events
  (`APPLICATION_STARTED`, `APPLICATION_STOPPED`, `REQUEST_RECEIVED`,
  `REQUEST_COMPLETED`, `HEALTH_CHECKED`). No event is published anywhere.
- `app/observability/metrics.py` declares `Counter`, `Gauge`, `Histogram`,
  and `Timer` as `Protocol` interfaces; no Prometheus or OpenTelemetry
  dependency was added.
- `app/observability/tracing.py` declares `Span` and `Tracer` as `Protocol`
  interfaces; no OpenTelemetry or Jaeger dependency was added.
- `ObservabilityMiddleware` runs for every request, derives the request ID
  from the request state (set by the request ID middleware), generates a
  fresh `UUID4` correlation ID, and stores a `RequestContext` on
  `request.state.context`. Runtime smoke tests confirm the context is
  populated and the `trace_id`/`user_id`/`organization_id` fields default
  to `None`.
- `register_middlewares()` registers `ObservabilityMiddleware`; the
  effective order is security headers, request ID, CORS, observability.
- `ruff check` and `ruff format --check` pass across `backend/app`.
- `mypy --strict` passes across `backend/app`.
- A runtime smoke test (application factory, `TestClient`, health request)
  succeeds and emits only the four lifecycle log lines; no request-context
  event logging was added.
- No authentication, metrics exporter, tracing backend, event bus, or new
  HTTP endpoint was created.

---

# Phase 1.10 Summary

## Files Created

- Dockerfile
- .dockerignore
- docker/development/docker-compose.yml

## Files Modified

- backend/README.md
- docs/PROJECT_STATUS.md

## Verification Results

- `Dockerfile` (repository root) targets Python 3.12, installs uv from the
  official uv image, creates `/app` as the working directory, runs uvicorn
  with `--reload` (hot reload) on `0.0.0.0:8000`, and executes as a
  non-root user (`twib`, uid 1000). The image is intentionally not
  optimized; production optimization is Phase 1.11.
- `.dockerignore` (repository root) whitelists the build context to the
  `backend/` subtree (`*`, `!backend/`, `!backend/**`) and re-excludes
  `backend/.venv/`, environment files, and caches, keeping the context
  small.
- `docker/development/docker-compose.yml` defines `backend`, `postgres`
  (17-alpine), `redis` (7-alpine), and `qdrant` (v1.14.0) on a single
  `twib-dev` bridge network with named volumes (`postgres_data`,
  `redis_data`, `qdrant_data`).
- The backend service reads `backend/.env` via `env_file` (the existing
  settings system) with container overrides for `HOST`/`PORT`, binds the
  `backend/app` source for hot reload, exposes `8000:8000`, and gates
  startup on healthy supporting services via `depends_on: service_healthy`.
- The compose file parses as valid YAML and uses standard Compose 2+
  constructs (`name`, `condition: service_healthy`, interpolation
  defaults).
- No secrets are hardcoded; supporting-service credentials default to dev
  values via interpolation and can be overridden from the environment.
- No production Dockerfile, production compose, Kubernetes, NGINX, CI/CD,
  Terraform, or Helm was created.
- No application source files were modified in this phase.

---

# Phase 1.10 Suggestions (Not Implemented)

- Docker could not be executed during this phase (per the phase rules), so
  the image build and `docker compose up` were not verified at runtime.
  Run `docker compose -f docker/development/docker-compose.yml config` and
  `docker compose up` after this phase to confirm the stack starts.
- The uv image is pinned to `ghcr.io/astral-sh/uv:latest` in the
  development Dockerfile. Pin a specific uv release for reproducible builds
  once the image is stabilized.
- `uv sync --all-groups` at build time re-locks when the manifest is newer
  than the copied `uv.lock` (the lockfile is currently stale after Phase
  1.9). Once `uv sync` is run manually, the Dockerfile could switch to
  `uv sync --all-groups --frozen` for deterministic installs.
- The backend runs with uvicorn's built-in stat reloader. Installing
  `uvicorn[standard]` (or adding `watchfiles`) would make `--reload` use
  the faster file watcher.
- Bind-mounted source is owned by the host user. On Linux hosts whose user
  is not uid 1000, the container user `twib` may lack write access to the
  mounted files (reads still work); a UID/GID build arg could resolve this.
- Supporting-service image tags (postgres 17, redis 7, qdrant v1.14.0)
  should be reviewed when the database and cache phases land and the
  services are actually used.
- The Qdrant health check probes the REST port with a bash TCP connect;
  if the image ever drops bash, an equivalent probe (for example against
  `/readyz`) would be needed.
- `docker/development/` hosts the compose file; a `docker/development/.env`
  could be added to centralize the supporting-service credential defaults
  documented in the README.

---

# Phase 1.9 Summary

## Files Created

- backend/tests/__init__.py
- backend/tests/conftest.py
- backend/tests/test_health.py
- backend/pytest.ini

## Files Modified

- backend/pyproject.toml
- backend/README.md
- docs/PROJECT_STATUS.md

## Dependencies Added

- pytest (dev group, `[dependency-groups] dev`)
- pytest-asyncio (dev group)
- pytest-cov (dev group)
- httpx (dev group)
- Lockfile (`uv.lock`) update deferred to manual verification via `uv sync`

## Verification Results

- `backend/pytest.ini` centralizes pytest configuration: `testpaths = tests`
  (discovery), `--cov=app --cov-report=term-missing` (coverage), and
  `asyncio_mode = strict` (async support for future `@pytest.mark.asyncio`
  tests).
- `backend/tests/` is a package (`__init__.py`), so pytest resolves the
  `app` package from the `backend/` root without path configuration.
- The reusable `client` fixture in `conftest.py` builds the application via
  `create_application()` and runs the FastAPI lifespan through the
  `TestClient` context manager; no test constructs its own client.
- `test_health.py` verifies `GET /api/v1/health` in four ways: HTTP status
  200, body validation against the shared `HealthResponse` schema, the JSON
  content type, and clean application startup/shutdown with the factory
  wiring on `app.state.settings` / `app.state.container`.
- `ruff check` and `ruff format --check` pass across `backend/app` and
  `backend/tests`.
- `mypy --strict` still passes across `backend/app`; no application source
  files were modified in this phase.
- Test files compile cleanly, and a runtime smoke test exercising the same
  code path as the tests (application factory, `TestClient`, health
  request) succeeds.
- No authentication, database, repository, service, agent, LLM, or
  workflow-engine tests were added; only infrastructure is covered.

---

# Phase 1.9 Suggestions (Not Implemented)

- `pytest`, `pytest-asyncio`, `pytest-cov`, and `httpx` were added to
  `pyproject.toml` but `uv.lock` was not updated (per the phase rules that
  forbid running `uv`). Run `uv sync` after this phase to pin the new dev
  dependencies, then `uv run pytest` to confirm the suite executes.
- Pytest configuration lives in `backend/pytest.ini`. For consistency with
  the single-config precedent of Phase 1.8, it could be moved into
  `[tool.pytest.ini_options]` in `pyproject.toml` in a future phase.
- The `client` fixture is function-scoped, so every test builds a fresh
  application. A module- or session-scoped fixture would reduce overhead
  once the suite grows, but function scope keeps tests isolated today.
- The pre-commit hooks still target only `backend/app`. Extending the Ruff
  hooks (and the MyPy hook) to `backend/tests/` would keep the test suite
  lint-clean in CI.
- Coverage has no failure threshold yet (`--cov-fail-under`). A threshold
  can be added once the suite covers more than the health endpoint.
- Only synchronous tests exist. pytest-asyncio is installed and configured
  in strict mode so later phases can add async tests with
  `@pytest.mark.asyncio`.
- `types-requests` remains installed preemptively; httpx ships its own type
  annotations, so once `requests` is actually used `types-requests` may be
  removed from the dev group.

---

# Phase 1.8 Summary

## Files Created

- .pre-commit-config.yaml

## Files Modified

- backend/pyproject.toml
- backend/app/schemas/common.py
- backend/app/schemas/pagination.py
- backend/app/schemas/response.py
- backend/app/schemas/__init__.py
- backend/app/api/openapi.py
- backend/app/core/environments.py
- backend/app/core/exceptions.py
- backend/app/core/handlers.py
- backend/app/core/logging.py
- backend/app/dependencies.py
- backend/app/middleware/request_id.py
- backend/app/middleware/security_headers.py
- backend/README.md
- docs/PROJECT_STATUS.md

## Dependencies Added

- ruff (dev group, `[dependency-groups] dev`)
- mypy (dev group)
- pre-commit (dev group)
- types-requests (dev group)
- Lockfile (`uv.lock`) update deferred to manual verification via `uv sync`

## Verification Results

- `ruff check` passes across `backend/app` (rule set: E, W, F, I, UP, B,
  SIM, C4, RUF, ASYNC, S, A; `ASYNC220` and `UP040` exempted).
- `ruff format --check` passes across `backend/app`.
- `mypy --strict` passes across `backend/app` with no `ignore_missing_imports`
  overrides; all runtime dependencies ship type annotations.
- `.pre-commit-config.yaml` at the repository root configures Ruff lint,
  Ruff format, and MyPy hooks for staged backend files.
- All configuration is centralized in `backend/pyproject.toml`; no
  `.ruff.toml`, `.mypy.ini`, or Black configuration was introduced.
- Runtime smoke test: `SuccessResponse[int]`, `PaginatedResponse[int]`,
  `TimestampedModel`, `Environment` (StrEnum), `_error_payload`, and
  `create_application()` all behave as before the annotation changes.
- No business logic, API behavior, authentication, database, AI, or Docker
  changes were made.

## Source Updates Required by the Tooling (type/format only)

The new toolchain exposed a small number of strict-mode and lint findings.
All fixes are semantic no-ops:

- `app/core/exceptions.py`: parameterized `details` as `dict[str, Any] | None`.
- `app/core/handlers.py`: parameterized `_error_payload`; registered the
  three narrow exception handlers through `cast(ExceptionHandler, ...)`
  because Starlette types handler callables against `Exception`.
- `app/core/logging.py`: `cast` the `structlog.get_logger(...).bind(...)`
  result to `structlog.BoundLogger`.
- `app/dependencies.py`: `cast` `request.app.state.container` to
  `ApplicationContainer`.
- `app/middleware/request_id.py`: annotated the `__init__` `app` parameter
  as `ASGIApp`.
- `app/middleware/security_headers.py`: annotated `headers` as
  `ClassVar[dict[str, str]]`.
- `app/core/environments.py`: `Environment` now inherits from `StrEnum`
  (UP042).
- `app/schemas/common.py`: `timezone.utc` replaced with the `UTC` alias
  (UP017).
- `app/schemas/response.py` and `app/schemas/pagination.py`: converted
  `SuccessResponse[T]` and `PaginatedResponse[T]` to PEP 695 type-parameter
  syntax (UP046); removed the now-unused `TypeVar`/`Generic` imports.
- `app/schemas/__init__.py`: sorted `__all__` (RUF022).
- `app/api/openapi.py` and `app/schemas/pagination.py`: reformatted by Ruff
  formatter for the 88-column limit (E501).

---

# Phase 1.8 Suggestions (Not Implemented)

- The pre-commit MyPy hook builds its own environment from
  `additional_dependencies`. A future phase could switch the hook to reuse
  the project's `.venv` (for example with `--python-executable`) so the
  hook and `uv run mypy` are guaranteed to resolve identical package
  versions.
- `types-requests` is installed preemptively; the current code never imports
  `requests`, so it is only needed once HTTP clients land in later phases.
- Ruff's `ASYNC220` exemption means async exception handlers that perform no
  `await` are not flagged. If those handlers are later converted to
  synchronous handlers (FastAPI supports both), the exemption could be
  removed.
- The `UP040` exemption keeps `typing.TypeAlias` aliases in
  `app/schemas/common.py` so their inline docstrings survive. If the aliases
  are ever converted to PEP 695 `type` statements, the exemption can be
  dropped.
- The hooks currently target only `backend/app`. Frontend hooks (ESLint,
  Prettier) and hooks for the remaining Python subsystems can be added to
  `.pre-commit-config.yaml` as those subsystems are built.
- The `[dependency-groups] dev` group is not yet reflected in `uv.lock`;
  running `uv sync` after this phase pins the new dev dependencies.

---

# Phase 1.7 Summary

## Files Created

- backend/app/schemas/__init__.py
- backend/app/schemas/common.py
- backend/app/schemas/pagination.py
- backend/app/schemas/response.py
- backend/app/api/tags.py
- backend/app/api/responses.py
- backend/app/api/openapi.py

## Files Modified

- backend/app/application.py
- backend/app/core/handlers.py
- backend/README.md
- docs/PROJECT_STATUS.md

## Dependencies Added

None

## Verification Results

- `SuccessResponse[T]`, `ErrorResponse`, `MessageResponse`, and
  `HealthResponse` serialize to the documented envelopes; `ErrorResponse`
  matches the JSON contract produced by the global exception handlers.
- `PaginatedResponse[T]` and `PaginationMeta` validate and serialize a
  generic page of items; no pagination logic was added.
- `EntityId`, `Timestamp`, `CreatedAt`, `UpdatedAt`, `Metadata`, and
  `TimestampedModel` are reusable across modules without duplication.
- `app/api/tags.py` exposes ten tag constants; `app/api/openapi.py` builds
  the ordered OpenAPI tag list from them.
- The OpenAPI document now includes the title (`TWIB`), version (`0.1.0`),
  description, contact, license (MIT), and the ten centralized tags.
  No routes were modified.
- Response helpers (`success`, `created`, `accepted`, `no_content`,
  `error`) return consistent envelopes with the correct status codes.
- `app/core/handlers.py` builds error bodies from the shared `ErrorResponse`
  schema; the output contract is byte-identical to the previous inline
  payload.
- No authentication, database, CRUD, or workflow logic was implemented.

---

# Phase 1.7 Suggestions (Not Implemented)

- The health endpoint still returns a bare dictionary instead of the new
  `HealthResponse` model. Wrapping it would align the route with the
  response-envelope standard once routes are allowed to be modified.
- `SuccessResponse` and `PaginatedResponse` duplicate the same `success`
  field. `PaginatedResponse` could inherit from `SuccessResponse[list[T]]`
  to reduce the duplication, but keeping them independent is clearer for
  the OpenAPI contract.
- The `openapi_tags` descriptions and the centralized tag constants could
  drift if new tags are added in only one place; a small mapping from
  constant to description in `app/api/openapi.py` keeps them in sync.
- Response helpers return `JSONResponse` directly, which bypasses FastAPI's
  `response_model` serialization. Future routers should declare
  `response_model=SuccessResponse[Model]` in their signatures so the
  OpenAPI document describes endpoint payloads accurately.
- `Metadata` is currently an unconstrained `dict[str, Any]`. A
  JSON-compatible validation (rejecting non-serializable values) would
  harden request schemas in later phases.
- Consider registering an OpenAPI generator hook to inject the response
  envelope as the default response for every endpoint, avoiding repetition
  across routers.

---

# Phase 1.6 Summary

## Files Created

- backend/app/middleware/__init__.py
- backend/app/middleware/cors.py
- backend/app/middleware/request_id.py
- backend/app/middleware/security_headers.py
- backend/app/middleware/registration.py

## Files Modified

- backend/app/application.py
- backend/README.md
- docs/PROJECT_STATUS.md

## Dependencies Added

None

## Verification Results

- `RequestIDMiddleware` generates a `UUID4`, stores it on
  `request.state.request_id`, binds it to the log context, and returns it
  in the `X-Request-ID` response header.
- `SecurityHeadersMiddleware` adds `X-Content-Type-Options`,
  `X-Frame-Options`, `Referrer-Policy`, and `X-XSS-Protection` to every
  response.
- CORS reads origins exclusively from `settings.cors_origins`; no origins
  are hardcoded.
- `register_middlewares()` is the only middleware registration point and is
  called once by `create_application()`.
- Effective middleware order (outermost first): security headers, request
  ID, CORS.
- No authentication, rate limiting, database, metrics, compression, or
  caching middleware was added.

---

# Suggestions (Not Implemented)

- `X-XSS-Protection` is deprecated in modern browsers and is only retained
  because this phase requires it. Consider dropping it (or replacing it
  with a proper Content-Security-Policy) once the CSP phase is implemented.
- The request ID middleware always generates a fresh `UUID4`. Honoring an
  inbound `X-Request-ID` (falling back to `UUID4` when absent) would
  improve correlation with upstream gateways for distributed tracing.
- `RequestIDMiddleware` and `SecurityHeadersMiddleware` are built on
  Starlette's `BaseHTTPMiddleware`. For very high throughput, equivalent
  pure-ASGI middleware avoids a small per-request overhead.
- Security headers could also be emitted at the reverse proxy / CDN layer
  in production for defense in depth.
- The empty top-level `backend/middleware/` scaffolding directory (README
  only) overlaps conceptually with `app/middleware/` and could be removed
  or consolidated to avoid confusion.

---

# Phase 1.5 Summary

## Files Created

- backend/app/core/error_codes.py
- backend/app/core/exceptions.py
- backend/app/core/handlers.py

## Files Modified

- backend/app/application.py
- backend/README.md
- docs/PROJECT_STATUS.md

## Dependencies Added

None

## Verification Results

- `TWIBException` and six generic exceptions carry `error_code`, `message`,
  `status_code`, and optional `details`.
- Global handlers cover `TWIBException`, `RequestValidationError`,
  `HTTPException`, and unhandled `Exception`.
- Every handler returns the consistent JSON error contract
  `{"success": false, "error": {"code", "message"}}`.
- Tracebacks are never exposed to clients; unhandled exceptions are logged
  server-side.
- Handlers are registered exactly once in `create_application()`; no
  duplicated registration.
- No middleware, authentication, database, or AI exceptions were added.

---

# Phase 1.4 Summary

## Files Created

- backend/app/container.py
- backend/app/dependencies.py

## Files Modified

- backend/pyproject.toml
- backend/app/application.py
- backend/README.md
- docs/PROJECT_STATUS.md

## Dependencies Added

- dependency-injector (added to `pyproject.toml`; lockfile update deferred
  to manual verification via `uv sync`)

## Verification Results

- `ApplicationContainer` defines singleton `settings` and factory `logger`
  providers backed by the existing configuration and logging systems.
- `create_application()` initializes the container and exposes it on
  `app.state.container`; settings are resolved through the container.
- `get_settings()` and `get_logger()` in `app/dependencies.py` resolve
  objects from the container through the request state; no new global
  singletons were introduced.
- No repositories, database connections, authentication, or AI components
  were implemented.

---

# Phase 1.3 Summary

## Files Created

- backend/app/core/logging.py

## Files Modified

- backend/pyproject.toml
- backend/uv.lock
- backend/app/application.py
- backend/app/lifecycle.py
- backend/README.md
- docs/PROJECT_STATUS.md

## Dependencies Added

- structlog (installed structlog 26.1.0 via uv)

## Verification Results

- `uv sync` resolves and installs successfully.
- `configure_logging()` installs the structlog pipeline once during application startup.
- Development renders colorized console lines; production renders JSON objects.
- `LOG_LEVEL` controls the active log level; invalid levels raise `ValueError`.
- `uv run uvicorn app.main:app --reload` starts successfully.
- Lifecycle logs appear: `Application Starting`, `Application Started`, `Application Shutting Down`, `Application Stopped`.
- `GET /api/v1/health` returns `200` with status healthy.
- No warnings and no duplicated log configuration.

---

# Phase 1.2 Summary

## Files Created

- backend/app/core/settings.py
- backend/app/core/config.py
- backend/app/core/environments.py
- backend/.env.example

## Files Modified

- backend/pyproject.toml
- backend/uv.lock
- backend/app/application.py
- backend/README.md
- docs/PROJECT_STATUS.md

## Dependencies Added

- pydantic-settings (installed pydantic-settings 2.14.2 and python-dotenv 1.2.2 via uv)

## Verification Results

- `uv sync` resolves and installs successfully.
- Settings load with defaults (`TWIB`, `Environment.DEVELOPMENT`, host/port/prefix defaults).
- `APP_ENV=production` selects the production environment.
- `CORS_ORIGINS` JSON list is parsed correctly.
- `application.state.settings` is populated by the factory.
- `uv run uvicorn app.main:app --reload` starts successfully.
- `GET /api/v1/health` returns `200` with status healthy.

---

# Commit Strategy

Commit after every completed sub-phase.

Examples

```
feat(phase-1.1): initialize FastAPI application

feat(phase-1.2): add configuration system

feat(phase-1.3): add structured logging

feat(phase-1.4): implement dependency injection

feat(phase-1.5): add global exception handling

feat(phase-1.6): add middleware infrastructure

feat(phase-1.7): add API foundation

feat(phase-1.8): add code quality infrastructure

feat(phase-1.9): add testing infrastructure

feat(phase-1.10): add docker development environment

feat(phase-1.11): add observability foundation

feat(phase-1.12): add docker production environment
```

---

# Success Criteria

Current phase is complete when:

- The foundation phases (1.1–1.12) are reviewed for consistency.
- Documentation and status reflect the completed foundation.
- The project structure remains clean.
- No authentication, database, AI, agents, or workflow engine has been
  implemented.

---

# Notes for Developers & AI Models

Before implementing any feature:

- Read the architecture.
- Follow PROJECT_RULES.md.
- Respect AI_SPECIFICATION.md.
- Do not modify locked decisions.
- Implement only the current phase.
- Stop after completing the assigned milestone.