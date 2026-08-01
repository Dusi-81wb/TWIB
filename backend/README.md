# TWIB Backend

## Purpose

The TWIB backend is the FastAPI service for the Total Workflow Intelligence
Builder platform. This repository currently contains the Phase 1.1 foundation
(application factory, versioned API routers, health endpoint, lifecycle
management), the Phase 1.2 configuration system (typed settings loaded from
environment variables), the Phase 1.3 structured logging system
(structlog with environment-aware rendering), the Phase 1.4 dependency
injection container (dependency-injector with container-backed FastAPI
dependencies), and the Phase 1.5 global exception handling system
(consistent JSON error responses for application, validation, HTTP, and
unhandled errors).

## Structure

```text
backend/
├── app/
│   ├── main.py            # Entry point (starts the application)
│   ├── application.py     # Application factory (create_application)
│   ├── lifecycle.py       # Startup/shutdown lifespan handler
│   ├── container.py       # Dependency injection container
│   ├── dependencies.py    # FastAPI dependencies (resolve from container)
│   ├── api/
│   │   ├── router.py      # Root API router (/api)
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── health.py  # Health endpoint (/api/v1/health)
│   ├── core/
│   │   ├── constants.py     # Application-wide constants
│   │   ├── environments.py  # Supported APP_ENV values
│   │   ├── settings.py      # ApplicationSettings (BaseSettings)
│   │   ├── config.py        # Singleton configuration loader
│   │   ├── logging.py       # Structured logging (structlog)
│   │   ├── error_codes.py   # Machine-readable error codes
│   │   ├── exceptions.py    # Application exception hierarchy
│   │   └── handlers.py      # Global exception handlers
│   └── shared/            # Cross-cutting utilities
├── .env.example           # Template for environment variables
├── pyproject.toml         # Project metadata and dependencies
├── uv.lock                # Locked dependency versions
├── .python-version        # Python 3.12
└── README.md
```

## Configuration

Configuration is managed with Pydantic Settings through the
`ApplicationSettings` class in `app/core/settings.py`.

- Every setting is typed and validated by Pydantic.
- Values are read from the process environment and a local `.env` file.
- The active environment is selected with `APP_ENV`
  (`development`, `testing`, or `production`).
- Settings are loaded exactly once by the singleton loader in
  `app/core/config.py` and exposed to the application on
  `app.state.settings`.

## Environment Variables

Copy `.env.example` to `.env` and fill in the placeholders:

```bash
cp .env.example .env
```

| Variable            | Purpose                                     | Default         |
| ------------------- | ------------------------------------------- | --------------- |
| `APP_NAME`          | Public application name                     | `TWIB`          |
| `APP_VERSION`       | Application version                         | `0.1.0`         |
| `APP_ENV`           | Environment (`development`/`testing`/`production`) | `development` |
| `DEBUG`             | Enable debug mode                           | `false`         |
| `HOST`              | Host the server binds to                    | `127.0.0.1`     |
| `PORT`              | Port the server listens on                  | `8000`          |
| `API_PREFIX`        | URL prefix for API routes                   | `/api`          |
| `LOG_LEVEL`         | Logging level                               | `INFO`          |
| `SECRET_KEY`        | Secret used for signing and cryptography    | *(empty)*       |
| `DATABASE_URL`      | PostgreSQL connection string                | *(empty)*       |
| `REDIS_URL`         | Redis connection string                     | *(empty)*       |
| `QDRANT_URL`        | Qdrant vector database URL                  | *(empty)*       |
| `OLLAMA_BASE_URL`   | Ollama LLM server base URL                  | *(empty)*       |
| `CORS_ORIGINS`      | Allowed CORS origins as a JSON list         | `[]`            |

Only placeholders are provided. No values are committed and no environment
file is required to run the application.

## How Configuration Works

1. The application factory initializes the dependency injection container
   and resolves the settings through its `settings` provider.
2. The `settings` singleton provider delegates to `get_settings()` from
   `app/core/config.py`, which instantiates `ApplicationSettings`. Pydantic
   populates it from environment variables (and a `.env` file if present).
3. The resulting immutable instance is cached by the loader and assigned to
   `application.state.settings`, providing one shared source of truth.
4. `APP_ENV` selects the environment. Invalid values raise a Pydantic
   `ValidationError` at startup.

The configuration system is self-contained. Middleware, authentication, and
databases are intentionally not part of this phase.

## Logging

Logging is built on [structlog](https://www.structlog.org/) and is
configured exactly once during application startup by
`configure_logging()` in `app/core/logging.py`. Every module obtains a
named logger with `get_logger(__name__)`.

### How Logging Works

1. `create_application()` in `app/application.py` loads the settings and
   calls `configure_logging(settings)` before the FastAPI instance is
   built.
2. `configure_logging()` installs a processor pipeline that enriches every
   event with a timestamp, log level, logger name, stack-trace information,
   and exception details, then renders the event.
3. The active environment selects the output format:

   - **Development** (`APP_ENV=development`): colorized, human-readable
     key/value lines on the console.
   - **Production** (`APP_ENV=production`): one JSON object per line,
     suitable for log aggregators such as Loki, Elasticsearch, or
     CloudWatch.

4. The logger used by the application lifespan in `app/lifecycle.py`
   emits the lifecycle events `Application Starting`, `Application
   Started`, `Application Shutting Down`, and `Application Stopped`.
5. Exceptions are captured through `logger.exception(...)`; the
   `format_exc_info` processor includes the formatted traceback in the
   structured event.

### How to Change the Log Level

The log level is controlled by the `LOG_LEVEL` environment variable
(`backend/.env.example`), which maps to `settings.log_level`. Use any
standard Python level name:

```bash
# backend/.env
LOG_LEVEL=DEBUG
```

Supported values: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. An
invalid value raises a `ValueError` at startup.

## Dependency Injection

Dependency injection is built on
[dependency-injector](https://python-dependency-injector.ets-labs.org/).
The object graph is owned by a single container, so components never
instantiate their collaborators directly.

### Application Container

The container is defined declaratively by the `ApplicationContainer` class
in `app/container.py`. Every collaborator is exposed through a provider.

Currently registered providers:

| Provider   | Scope      | Resolves                                          |
| ---------- | ---------- | ------------------------------------------------- |
| `settings` | Singleton  | The shared `ApplicationSettings` instance         |
| `logger`   | Factory    | A named structlog logger                          |

The container is created and initialized by `create_application()` in
`app/application.py` and exposed to every component through
`app.state.container`. `create_application()` resolves the settings through
the container and uses them to configure structured logging.

### FastAPI Dependencies

FastAPI dependency functions in `app/dependencies.py` retrieve objects from
the container through the request state:

- `get_settings()` resolves the application settings singleton.
- `get_logger()` resolves a named structured logger.
- `get_container()` returns the container itself.

```python
from fastapi import Depends

from app.core.settings import ApplicationSettings
from app.dependencies import get_settings


@app.get("/example")
def example(settings: ApplicationSettings = Depends(get_settings)) -> dict:
    return {"app_name": settings.app_name}
```

No module creates global singletons. Objects are always resolved through
the container, which keeps the graph in one place and enables overrides in
tests.

### How Future Services Are Registered

New services are registered in `ApplicationContainer` as additional
providers. Stateless services use `providers.Singleton`; stateful or
request-scoped objects use `providers.Factory`. Repositories, databases,
and infrastructure adapters will follow the same pattern in later phases.

```python
from dependency_injector import containers, providers

from app.core.config import get_settings as _load_settings
from app.core.logging import get_logger as _resolve_logger
from app.services.workflow import WorkflowService


class ApplicationContainer(containers.DeclarativeContainer):
    settings = providers.Singleton(_load_settings)
    logger = providers.Factory(_resolve_logger)

    workflow_service = providers.Singleton(WorkflowService)
```

The container is the single place where the object graph is assembled. No
other module should wire dependencies directly.

## Error Handling

Every error response follows one consistent JSON contract. Python
tracebacks are never exposed to clients; unexpected failures are logged
server-side.

### Error Response Contract

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Workflow not found."
  }
}
```

The optional `details` field is included when an error carries structured
information.

### Exception Hierarchy

The base `TWIBException` in `app/core/exceptions.py` defines every error:

- `error_code` - a stable, machine-readable code from
  `app/core/error_codes.py`.
- `message` - a human-readable description.
- `status_code` - the HTTP status returned to the client.
- `details` - optional structured information.

Generic infrastructure exceptions are provided:

| Exception                   | Code                  | Status |
| --------------------------- | --------------------- | ------ |
| `ValidationException`       | `VALIDATION_ERROR`    | 400    |
| `UnauthorizedException`     | `UNAUTHORIZED`        | 401    |
| `ForbiddenException`        | `FORBIDDEN`           | 403    |
| `NotFoundException`         | `RESOURCE_NOT_FOUND`  | 404    |
| `ConflictException`         | `CONFLICT`            | 409    |
| `InternalServerException`   | `INTERNAL_SERVER_ERROR` | 500  |
| `ServiceUnavailableException` | `SERVICE_UNAVAILABLE` | 503   |

```python
from app.core.exceptions import NotFoundException

raise NotFoundException("Workflow not found.")
```

### Global Exception Handlers

`app/core/handlers.py` registers handlers for four categories:

1. `TWIBException` - application exceptions, rendered from the exception
   attributes.
2. `RequestValidationError` - FastAPI request validation failures, rendered
   as `422` with the validation details.
3. `HTTPException` - HTTP errors raised by FastAPI and Starlette.
4. `Exception` - any unhandled exception, logged server-side and returned
   as a generic `500`.

`register_exception_handlers(application)` is called once by
`create_application()` in `app/application.py`. No handler is registered
twice, and no middleware is involved.

## How to Install

Prerequisites:

- [uv](https://docs.astral.sh/uv/) (package manager)
- Python 3.12 (managed automatically by uv)

Install dependencies:

```bash
cd backend
uv sync
```

This creates a virtual environment and installs all locked dependencies.

## How to Run

Start the development server:

```bash
cd backend
uv run uvicorn app.main:app --reload
```

Verify the health endpoint:

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "TWIB",
  "version": "0.1.0"
}
```

Interactive API documentation is available at:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

## Development Notes

- The FastAPI instance is created only through `create_application()` in
  `app/application.py`; it is never defined as a global.
- `app/main.py` is the sole entry point and only starts the application.
- API routes are versioned under `/api/v1`.
- The dependency injection container is created in `create_application()`
  and exposed on `application.state.container`. Settings and loggers are
  resolved through the container via `app/dependencies.py`.
- Settings are resolved through the container's `settings` provider and
  exposed on `application.state.settings`.
- Structured logging is configured once in `create_application()` through
  `configure_logging()` and is available to every module through
  `get_logger(__name__)`.
- Lifecycle handlers log startup and shutdown events. No database, cache,
  or other infrastructure is initialized in this phase.
- Global exception handlers are registered once in `create_application()`
  through `register_exception_handlers()` and return a consistent JSON
  error response without exposing tracebacks.
- Logging, dependency injection, and exception handling are the
  cross-cutting infrastructure implemented so far. Middleware,
  authentication, and request logging are intentionally deferred to later
  phases.
- Follow the project coding guidelines (PEP 8, type hints, Google-style
  docstrings). Do not add code outside the current phase.
