# ADR-0008 Backend Package Layout

## Status

Accepted

## Context

PROJECT_RULES Rule 3 freezes the folder structure: no structural change is allowed
without an ADR. During Phase 1 the backend was implemented with all FastAPI
application code living under a single `backend/app/` package (import prefix
`app.*`), while `folder_structure.md` and `coding_guidelines.md` still documented
top-level backend packages (`backend/api`, `backend/services`, `backend/core`,
...) and imports such as `backend.services.user.service`.

The result is a divergence:

- Real, implemented code lives under `backend/app/`.
- README-only scaffolding directories still exist at `backend/api`, `backend/config`,
  `backend/dependencies`, `backend/exceptions`, `backend/middleware`, `backend/schemas`,
  `backend/services`, `backend/utils`, and `backend/websocket`.

These two parallel "source trees" are confusing for contributors and for AI coding
assistants, and risk scattering Phase 2+ code across both locations. The Phase 1.13
architecture audit flagged this as the primary structural issue to resolve before
Phase 2.

## Decision

All FastAPI web-application code lives in the single `backend/app/` package and is
imported as `app.*`. The entrypoint is `app.main:app`. Tests live in
`backend/tests/` and import `app.*`.

Implemented subpackages:

```
backend/app/
├── __init__.py
├── main.py            # Uvicorn entrypoint (app.main:app)
├── application.py     # FastAPI application factory
├── container.py       # DI container (dependency-injector)
├── dependencies.py    # Shared FastAPI dependencies
├── lifecycle.py       # Startup/shutdown logging
├── api/               # Routers, tags, OpenAPI, response helpers
│   ├── v1/
│   │   └── health.py
│   ├── router.py
│   ├── tags.py
│   ├── openapi.py
│   └── responses.py
├── core/              # Settings, config, logging, exceptions, handlers
├── middleware/        # Cross-cutting concerns + central registration
├── observability/     # Metrics/tracing protocols, events, request context
├── schemas/           # Pydantic contracts (common, pagination, response)
└── shared/            # Shared helpers
```

Future backend modules are added as subpackages of `app/` (for example
`app/services`, `app/repositories`, `app/infrastructure`) using the same
single-package convention.

The legacy README-only directories directly under `backend/` (`api`, `config`,
`dependencies`, `exceptions`, `middleware`, `schemas`, `services`, `utils`,
`websocket`) are **deprecated**. No new code may be placed in them. They will be
removed as the corresponding `app/` subpackages mature; Phase 2 cleanup will
delete them.

Top-level repository packages (`agents/`, `workflows/`, `llm/`, `database/`,
`auth/`, `cache/`, `vector_db/`, `storage/`, `payments/`, `analytics/`, `realtime/`,
`security/`, `frontend/`) remain reserved for their future domain, engine, and
infrastructure modules as documented in `folder_structure.md`. The FastAPI
application (`app.*`) consumes those packages only through protocols and the DI
container, per the Clean Architecture dependency rule (ADR-0001).

## Alternatives Considered

- **Keep the documented top-level `backend/api`, `backend/services`, ... layout and
  move code out of `app/`:** rejected. Would churn all Phase 1 code, contradict the
  committed structure, and add nesting without architectural benefit.
- **Keep both `app/` and the scaffolding dirs, treating the docs as authoritative:**
  rejected. Two source trees guarantee code scatter and inconsistent imports.
- **Flat modules directly in `backend/`:** rejected. A single `app` import root is
  cleaner and matches FastAPI/uv conventions.

## Consequences

- The import prefix `app.*` is the single convention for backend application code
  (isort `known-first-party = ["app"]` is already configured).
- `folder_structure.md` and `coding_guidelines.md` are updated to describe the
  `app/` layout (this phase).
- The scaffolding directories at `backend/` are deprecated and scheduled for
  removal; no code may be added there.
- New backend modules must be placed under `app/`, satisfying PROJECT_RULES
  Rule 3 through this ADR.
