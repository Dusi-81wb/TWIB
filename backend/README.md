# TWIB Backend

## Purpose

The TWIB backend is the FastAPI service for the Total Workflow Intelligence
Builder platform. This repository currently contains the Phase 1.1 foundation
(application factory, versioned API routers, health endpoint, lifecycle
management), the Phase 1.2 configuration system (typed settings loaded from
environment variables), the Phase 1.3 structured logging system
(structlog with environment-aware rendering), the Phase 1.4 dependency
injection container (dependency-injector with container-backed FastAPI
dependencies), the Phase 1.5 global exception handling system
(consistent JSON error responses for application, validation, HTTP, and
unhandled errors), the Phase 1.6 middleware infrastructure (request
IDs, security headers, and settings-driven CORS), and the Phase 1.7 API
foundation (reusable response and pagination schemas, centralized API
tags, response helper functions, and a configured OpenAPI document), and
the Phase 1.8 code quality infrastructure (Ruff linting and formatting,
MyPy strict type checking, and pre-commit hooks), and the Phase 1.9
testing infrastructure (pytest, pytest-asyncio, coverage, and a reusable
httpx-based test client), and the Phase 1.10 Docker development
environment (a development image using uv, and a Docker Compose stack for
the backend with PostgreSQL, Redis, and Qdrant), and the Phase 1.11
observability foundation (a request context object, event definitions, and
the metrics and tracing interfaces), and the Phase 1.12 Docker production
environment (a multi-stage Dockerfile with a minimal production runtime
image and a production Docker Compose stack), and the Phase 2.1 domain
foundation (framework-independent base classes for entities, aggregates,
value objects, domain events, and identities, plus the domain exception
hierarchy), and the Phase 2.2 domain value objects (reusable, immutable,
self-validating value objects for identifiers, emails, names, slugs,
timestamps, URLs, versions, money, and metadata), and the Phase 2.3 user
domain (the User aggregate root built from the value objects, with user
statuses, roles, domain events, and business-rule exceptions).

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
│   │   ├── responses.py   # Centralized response helpers
│   │   ├── tags.py        # Centralized OpenAPI tags
│   │   ├── openapi.py     # OpenAPI metadata (description, contact, license, tags)
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── health.py  # Health endpoint (/api/v1/health)
│   ├── schemas/
│   │   ├── __init__.py    # Public schema exports
│   │   ├── common.py      # EntityId, timestamps, Metadata, TimestampedModel
│   │   ├── pagination.py  # PaginationMeta, PaginatedResponse[T]
│   │   └── response.py    # SuccessResponse, ErrorResponse, MessageResponse, HealthResponse
│   ├── core/
│   │   ├── constants.py     # Application-wide constants
│   │   ├── environments.py  # Supported APP_ENV values
│   │   ├── settings.py      # ApplicationSettings (BaseSettings)
│   │   ├── config.py        # Singleton configuration loader
│   │   ├── logging.py       # Structured logging (structlog)
│   │   ├── error_codes.py   # Machine-readable error codes
│   │   ├── exceptions.py    # Application exception hierarchy
│   │   └── handlers.py      # Global exception handlers
│   ├── middleware/
│   │   ├── __init__.py        # Middleware package exports
│   │   ├── cors.py            # CORS from application settings
│   │   ├── request_id.py      # X-Request-ID generation
│   │   ├── security_headers.py# Security response headers
│   │   ├── observability.py   # Request context middleware
│   │   └── registration.py    # Central middleware registration
│   ├── observability/         # Observability primitives
│   │   ├── __init__.py        # Observability package exports
│   │   ├── request_context.py # Request-scoped context object
│   │   ├── events.py          # Event definitions
│   │   ├── metrics.py         # Metrics interfaces (Counter, Gauge, ...)
│   │   └── tracing.py         # Tracing interfaces (Span, Tracer)
│   ├── domain/                # Domain layer (pure Python, no frameworks)
│   │   ├── __init__.py        # Public domain exports
│   │   ├── base.py            # Aggregated abstract base classes
│   │   ├── entity.py          # Identity[T], Entity
│   │   ├── aggregate.py       # AggregateRoot
│   │   ├── value_object.py    # ValueObject
│   │   ├── event.py           # DomainEvent
│   │   │   ├── exceptions.py      # Domain exception hierarchy
│   │   ├── value_objects/     # Concrete domain value objects
│   │   │   ├── __init__.py    # Public value object exports
│   │   │   ├── id.py          # UuidIdentity
│   │   │   ├── email.py       # Email
│   │   │   ├── name.py        # Name
│   │   │   ├── slug.py        # Slug
│   │   │   ├── timestamp.py   # Timestamp
│   │   │   ├── url.py         # Url
│   │   │   ├── version.py     # Version
│   │   │   ├── money.py       # Money
│   │   │   └── metadata.py    # Metadata
│   │   └── users/             # User domain aggregate
│   │       ├── __init__.py    # Public user domain exports
│   │       ├── user.py        # User aggregate root
│   │       ├── role.py        # UserRole
│   │       ├── status.py      # UserStatus
│   │       ├── events.py      # User domain events
│   │       └── exceptions.py  # User business-rule exceptions
│   └── shared/            # Cross-cutting utilities
├── .env.example           # Template for environment variables
├── pyproject.toml         # Project metadata and dependencies
├── pytest.ini             # Pytest configuration (discovery, coverage, async)
├── tests/
│   ├── __init__.py        # Marks the directory as a package
│   ├── conftest.py        # Shared fixtures (reusable TestClient)
│   └── test_health.py     # Health endpoint tests
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

## Observability

Observability primitives live in `app/observability/`. This phase defines
the request context object and the interfaces for metrics and tracing; no
exporter or backend is wired in yet.

### Request Context

`RequestContext` in `app/observability/request_context.py` is the
identifying metadata for a single request:

| Field            | Type            | Description                                  |
| ---------------- | --------------- | -------------------------------------------- |
| `request_id`     | `str`           | Unique identifier for the request            |
| `timestamp`      | `datetime`      | Time the request entered the application     |
| `correlation_id` | `str`           | Identifier grouping related requests         |
| `trace_id`       | `str | None`    | Trace ID once a tracing backend is wired in  |
| `user_id`        | `str | None`    | Authenticated user, when available           |
| `organization_id`| `str | None`    | Authenticated organization, when available   |

`ObservabilityMiddleware` builds the context for every request and stores
it on `request.state.context`. Route handlers and dependencies can read it
through the request state:

```python
from starlette.requests import Request

from app.observability.request_context import RequestContext


@app.get("/example")
def example(request: Request) -> dict:
    context: RequestContext = request.state.context
    return {"request_id": context.request_id}
```

The `trace_id`, `user_id`, and `organization_id` fields remain `None` until
tracing and authentication are implemented.

### Event Definitions

`app/observability/events.py` defines the names of the application events
as an `EventType` enumeration: `APPLICATION_STARTED`, `APPLICATION_STOPPED`,
`REQUEST_RECEIVED`, `REQUEST_COMPLETED`, and `HEALTH_CHECKED`. The events
are declared so producers and consumers agree on names before any publishing
infrastructure exists; no event is emitted in this phase.

### Future Metrics

`app/observability/metrics.py` declares the interfaces for the metrics
instruments as `Protocol`s:

| Interface   | Methods                                  |
| ----------- | ---------------------------------------- |
| `Counter`   | `add(amount=1)`                          |
| `Gauge`     | `set(value)`, `inc()`, `dec()`           |
| `Histogram` | `observe(value)`                         |
| `Timer`     | `time()` (context manager)               |

No concrete implementation exists yet. A Prometheus or OpenTelemetry
adapter will implement these protocols in a later phase.

### Future Tracing

`app/observability/tracing.py` declares the tracing interfaces as
`Protocol`s:

| Interface | Methods                                      |
| --------- | -------------------------------------------- |
| `Span`    | `set_attribute(key, value)`, `end()`         |
| `Tracer`  | `start_span(name)`, `span(name)` (context manager) |

No concrete implementation exists yet. An OpenTelemetry or Jaeger adapter
will implement these protocols in a later phase.

## Domain Layer

The domain layer lives in `app/domain/` and contains the enterprise business
rules of the platform. It is **pure Python**: it imports no FastAPI, Pydantic,
SQLAlchemy, or any other framework, so it never depends on an outer layer and
can be reused by every future module (Clean Architecture).

### Files

| File             | Contents                                          |
| ---------------- | ------------------------------------------------- |
| `base.py`        | Aggregates the abstract base classes              |
| `entity.py`      | `Identity[T]`, `Entity`                           |
| `aggregate.py`   | `AggregateRoot`                                   |
| `value_object.py`| `ValueObject`                                     |
| `event.py`       | `DomainEvent`                                     |
| `exceptions.py`  | Domain exception hierarchy                        |
| `value_objects/` | Concrete, reusable value objects (package)        |
| `users/`         | User aggregate, roles, statuses, events, exceptions |

### Entities

An entity is a domain object defined by its identity rather than its state.
`Entity` (in `app/domain/entity.py`) stores a stable `Identity[T]` and
implements equality and hashing based on the type and identity, so two
entities with the same identity are equal even if their state differs:

```python
class User(Entity[uuid.UUID]):
    def __init__(self, id_: Identity[uuid.UUID], name: str) -> None:
        super().__init__(id_)
        self.name = name
```

`Identity[T]` is an immutable value wrapper around the underlying identifier
(UUID, string, or integer) and is compared by value.

### Aggregates

`AggregateRoot` (in `app/domain/aggregate.py`) is an entity that acts as the
consistency boundary for a cluster of entities and value objects. While its
business rules are applied it records `DomainEvent` instances with
`record_event(event)` and hands them to the outside world exactly once with
`pull_domain_events()`:

```python
order = Order(Identity(order_id))
order.mark_paid()
for event in order.pull_domain_events():
    event_bus.publish(event)  # done by an outer layer
```

### Value Objects

`ValueObject` (in `app/domain/value_object.py`) is an immutable object defined
entirely by its attributes. Equality, hashing, and representation are compared
by value, so two value objects with the same attributes are interchangeable.
Subclasses are declared as frozen dataclasses with `eq=False`:

```python
@dataclass(frozen=True, eq=False)
class Email(ValueObject):
    value: str
```

### Concrete Value Objects

The reusable value objects live in `app/domain/value_objects/` and are
imported from a single location:

```python
from app.domain.value_objects import Email, Money, UuidIdentity, Version
```

Every value object is immutable, validates its value at construction, is
compared and hashed by value, and has a meaningful string representation.
They depend only on the Python standard library (no dataclasses, FastAPI,
Pydantic, or SQLAlchemy); immutability is enforced by overriding
`__setattr__` to reject assignments after construction.

| File         | Class          | Stores / validates                                          |
| ------------ | -------------- | ----------------------------------------------------------- |
| `id.py`      | `UuidIdentity` | A UUID4 entity identity; `generate()` and `parse()` helpers |
| `email.py`   | `Email`        | A normalized, syntactically valid email address             |
| `name.py`    | `Name`         | A trimmed, non-empty display name (max 120 characters)      |
| `slug.py`    | `Slug`         | A lowercase URL-friendly slug (`a-z0-9` and single hyphens) |
| `timestamp.py`| `Timestamp`   | A timezone-aware UTC moment; `now()` and `parse()` helpers  |
| `url.py`     | `Url`          | An absolute `http`/`https` URL                              |
| `version.py` | `Version`      | A `major.minor.patch` semantic version; `parse()` helper    |
| `money.py`   | `Money`        | A `Decimal` amount with an ISO 4217 currency code           |
| `metadata.py`| `Metadata`     | An immutable string key/value metadata map                  |

```python
from decimal import Decimal

from app.domain.value_objects import Email, Money, UuidIdentity, Version

user_id = UuidIdentity.generate()
parsed_id = UuidIdentity.parse("123e4567-e89b-12d3-a456-426614174000")
email = Email("User@Example.com")          # normalized to user@example.com
version = Version.parse("1.2.3")
price = Money(Decimal("19.99"), "USD")
```

Invalid values raise `InvalidValue` (a `DomainException` subclass) at
construction instead of being silently accepted, so entities can never hold a
malformed value object.

### User Aggregate

The core business entity of TWIB is the `User` aggregate root in
`app/domain/users/`, imported from a single location:

```python
from app.domain.users import User, UserRole, UserStatus
from app.domain.value_objects import Email, Name, UuidIdentity
```

`User` extends `AggregateRoot` and is built entirely from the Phase 2.2 value
objects. Its state is exposed only through read-only properties (never as
mutable attributes), and every change goes through a domain method that
validates the operation, records a domain event, and bumps the version:

| Property      | Type          | Meaning                                  |
| ------------- | ------------- | ---------------------------------------- |
| `user_id`     | `UuidIdentity`| Stable UUID identity of the user         |
| `email`       | `Email`       | The user's email address                 |
| `display_name`| `Name`        | The user's display name                  |
| `created_at`  | `Timestamp`   | When the user was created (UTC)          |
| `updated_at`  | `Timestamp`   | When the user was last changed (UTC)     |
| `status`      | `UserStatus`  | Current lifecycle state                  |
| `role`        | `UserRole`    | Role the user holds in the organization  |
| `metadata`    | `Metadata`    | Key/value metadata map (immutable)       |
| `version`     | `Version`     | Optimistic-locking version (auto-bumped) |

```python
user = User(
    user_id=UuidIdentity.generate(),
    email=Email("user@example.com"),
    display_name=Name("Ada Lovelace"),
)
user.activate()
user.change_display_name(Name("Grace Hopper"))
for event in user.pull_domain_events():
    pass  # publishing is done by an outer layer
```

The domain methods are `activate()`, `deactivate()`, `suspend()`, `restore()`,
`delete()`, `change_display_name()`, `change_email()`, `update_metadata()`,
and `increment_version()`. Every successful mutation refreshes `updated_at`
and bumps `version` (one patch); call `increment_version()` directly only for
out-of-band changes.

#### Statuses

`UserStatus` (in `app/domain/users/status.py`) is a `StrEnum`:

| Status      | Value       | Meaning                                        |
| ----------- | ----------- | ---------------------------------------------- |
| `PENDING`   | `"pending"` | Created but not activated yet                  |
| `ACTIVE`    | `"active"`  | Can use the platform                           |
| `SUSPENDED` | `"suspended"`| Temporarily suspended                         |
| `DISABLED`  | `"disabled"`| Deactivated; cannot sign in                    |
| `DELETED`   | `"deleted"` | Deleted; terminal state                        |

#### Roles

`UserRole` (in `app/domain/users/role.py`) is a `StrEnum`. Only the roles are
modelled; permissions are intentionally out of scope:

| Role     | Value      |
| -------- | ---------- |
| `OWNER`  | `"owner"`  |
| `ADMIN`  | `"admin"`  |
| `MEMBER` | `"member"` |
| `VIEWER` | `"viewer"` |

#### User Domain Events

`app/domain/users/events.py` defines the domain events, all subclasses of
`DomainEvent` that carry the affected `user_id`:

| Event              | Recorded by                                  |
| ------------------ | -------------------------------------------- |
| `UserCreated`      | construction of a new user                   |
| `UserActivated`    | `activate()`                                 |
| `UserSuspended`    | `suspend()`                                  |
| `UserDeleted`      | `delete()`                                   |
| `UserEmailChanged` | `change_email()` (carries new and previous)  |
| `UserNameChanged`  | `change_display_name()` (carries new/previous) |

The aggregate only records events; there is no event bus in this phase.

#### User Business-Rule Exceptions

`app/domain/users/exceptions.py` defines the user business-rule exceptions,
all subclasses of `BusinessRuleViolation`:

| Exception             | Raised when                                   |
| --------------------- | --------------------------------------------- |
| `InvalidUserState`    | An operation is invalid in the current state  |
| `EmailAlreadyAssigned`| An email is already assigned to the user      |
| `CannotSuspendOwner`  | An owner user is suspended                    |
| `UserAlreadyActive`   | An already-active user is activated           |

### Domain Events

`DomainEvent` (in `app/domain/event.py`) is an immutable record that something
happened in the domain. Every occurrence carries a unique `event_id`, a UTC
`occurred_at` timestamp, and a derived `event_name`. Base fields are
keyword-only, so concrete events declare their payload fields without defaults:

```python
@dataclass(frozen=True, eq=False, repr=False)
class WorkflowCreated(DomainEvent):
    workflow_id: Identity[uuid.UUID]
```

The domain layer only *records* events. Publishing, emails, notifications, and
analytics belong to outer layers.

### Domain Exceptions

`app/domain/exceptions.py` defines the framework-independent domain exception
hierarchy:

| Exception              | Meaning                                             |
| ---------------------- | --------------------------------------------------- |
| `DomainException`      | Base class for all domain errors (`message`, `details`) |
| `BusinessRuleViolation`| An enterprise business rule or invariant was broken |
| `EntityNotFound`       | A requested entity does not exist                   |
| `InvalidOperation`     | An operation is not valid in the current state      |
| `InvalidValue`         | A value object was constructed with an invalid value |

Outer layers translate these into their own error contract (for example the
FastAPI `TWIBException` hierarchy in `app/core/exceptions.py`).

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

## Middleware

Middleware lives in `app/middleware/`. All middleware is registered
centrally by `register_middlewares(application, settings)` in
`app/middleware/registration.py`, which the application factory calls once.
No middleware is added directly in `app/application.py`.

The effective request/response order (outermost first) is:

1. Security headers
2. Request ID
3. CORS
4. Observability

### Request IDs

`RequestIDMiddleware` in `app/middleware/request_id.py`:

- Generates a unique `UUID4` for every request.
- Stores it on `request.state.request_id`.
- Binds it to the structured log context as `request_id`, so every log
  event for the request carries it.
- Echoes the same value back in the `X-Request-ID` response header.

### Observability

`ObservabilityMiddleware` in `app/middleware/observability.py` builds a
`RequestContext` for every request and stores it on
`request.state.context`. The context carries the request ID assigned by the
request ID middleware, the time the request entered the application, and a
fresh `UUID4` correlation ID. Future authentication and tracing will fill
the `user_id`, `organization_id`, and `trace_id` fields. See
[Observability](#observability-1) below.

### Security Headers

`SecurityHeadersMiddleware` in `app/middleware/security_headers.py` adds
these headers to every response:

| Header                    | Value                        |
| ------------------------- | ---------------------------- |
| `X-Content-Type-Options`  | `nosniff`                    |
| `X-Frame-Options`         | `DENY`                       |
| `Referrer-Policy`         | `no-referrer`                |
| `X-XSS-Protection`        | `1; mode=block`              |

Content Security Policy (CSP) is intentionally deferred to a later phase.

### CORS

CORS is configured in `app/middleware/cors.py` using FastAPI's
`CORSMiddleware`. Allowed origins are read from the `CORS_ORIGINS` setting
(`settings.cors_origins`) and are never hardcoded:

```bash
# backend/.env
CORS_ORIGINS=["https://app.example.com"]
```

## API Foundation

The API foundation defines the standards every future endpoint follows. It
consists of reusable schemas, centralized tags, response helpers, and a
configured OpenAPI document. No business endpoints were added in this
phase.

### Response Models

Reusable Pydantic response models live in `app/schemas/response.py`:

| Model            | Purpose                                            |
| ---------------- | -------------------------------------------------- |
| `SuccessResponse[T]` | Successful response envelope: `{"success": true, "data": ...}` |
| `ErrorResponse`  | Error envelope: `{"success": false, "error": {...}}` |
| `MessageResponse` | Success envelope carrying only a message           |
| `HealthResponse` | Health check response body                          |

The generic `SuccessResponse[T]` wraps any payload type. `ErrorResponse`
uses `ErrorDetail`, which mirrors the JSON contract produced by the global
exception handlers in `app/core/handlers.py`, so every error response has
one source of truth.

### Common Schemas

`app/schemas/common.py` provides reusable primitives:

- `EntityId` - a UUID identifier alias used for entity primary keys.
- `Timestamp`, `CreatedAt`, `UpdatedAt` - datetime aliases for time fields.
- `Metadata` - an arbitrary key/value dict alias.
- `TimestampedModel` - a base model that adds `created_at` and `updated_at`.

These are shared across all modules so schemas never redefine common field
types.

### Pagination

`app/schemas/pagination.py` provides `PaginationMeta` and the generic
`PaginatedResponse[T]`. The models describe the shape of a paginated list
response and contain no pagination logic; page calculation belongs to
repositories and services in later phases.

```python
class PaginatedResponse(BaseModel, Generic[T]):
    success: bool = True
    data: list[T]
    pagination: PaginationMeta
```

### API Tags

All OpenAPI tags are defined as constants in `app/api/tags.py`. Every
future router declares its tag from this module so tag names stay
consistent:

| Constant           | Value            |
| ------------------ | ---------------- |
| `HEALTH`           | `health`         |
| `AUTHENTICATION`   | `authentication` |
| `USERS`            | `users`          |
| `ORGANIZATIONS`    | `organizations`  |
| `WORKFLOWS`        | `workflows`      |
| `AGENTS`           | `agents`         |
| `BILLING`          | `billing`        |
| `ADMIN`            | `admin`          |
| `ANALYTICS`        | `analytics`      |
| `STORAGE`          | `storage`        |

### Response Helpers

`app/api/responses.py` provides centralized helpers that build consistent
response bodies from the shared schemas:

| Helper                | HTTP Status | Envelope                                  |
| --------------------- | ----------- | ----------------------------------------- |
| `success(data)`       | `200`       | `{"success": true, "data": ...}`          |
| `created(data)`       | `201`       | `{"success": true, "data": ...}`          |
| `accepted(data=None)` | `202`       | `{"success": true, "data": ...}`          |
| `no_content()`        | `204`       | empty body                                |
| `error(code, msg, ...)` | `400`     | `{"success": false, "error": {...}}`      |

### OpenAPI

OpenAPI metadata is centralized in `app/api/openapi.py` and wired into the
FastAPI instance by `create_application()`. The document now configures:

- **Title** - `TWIB`
- **Version** - `0.1.0`
- **Description** - a summary of the platform and the response envelope
  contract.
- **Contact** - TWIB (GitHub repository).
- **License** - MIT.
- **Tags** - the ten centralized tags with descriptions.

Routes were not modified; only the API document metadata was improved.

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

## Docker Development

A development-oriented Docker setup is included so the backend and its
supporting services (PostgreSQL, Redis, Qdrant) run locally in containers.

### Files

- `Dockerfile` (repository root) - a Python 3.12 multi-stage image with two
  stages. The default `development` stage is the development image using
  uv: it installs runtime and development dependencies, runs uvicorn with
  hot reload (`--reload`) as a non-root user, and exposes port `8000`. The
  `runtime` stage is the minimal production image (no hot reload) and is
  selected by the production stack.
- `docker/development/docker-compose.yml` - the development stack:
  `backend`, `postgres`, `redis`, and `qdrant` on a single bridge network
  with named volumes for persistent data.
- `.dockerignore` (repository root) - keeps the build context small by
  sending only the backend subtree to the Docker daemon.

### Prerequisites

- Docker 24+
- Docker Compose 2+

The backend reads its configuration from `backend/.env` through the
existing settings system. Create it first from the template:

```bash
cd backend
cp .env.example .env
```

### Starting Containers

```bash
cd docker/development
docker compose up
```

This builds the backend image, starts all four services, and runs the
backend with hot reload. The API is available at
<http://localhost:8000/api/v1/health>.

To start the stack in the background:

```bash
docker compose up -d
```

### Stopping Containers

```bash
docker compose down
```

Named volumes keep PostgreSQL, Redis, and Qdrant data across restarts. To
stop the stack and remove the data volumes too:

```bash
docker compose down -v
```

### Useful Commands

| Command                                         | Purpose                                    |
| ----------------------------------------------- | ------------------------------------------ |
| `docker compose build`                          | Rebuild the backend image                  |
| `docker compose up -d`                          | Start the stack in the background          |
| `docker compose logs -f backend`                | Follow backend logs                        |
| `docker compose exec backend uv run pytest`     | Run the test suite in the container        |
| `docker compose exec backend sh`                | Open a shell in the backend container      |
| `docker compose down`                           | Stop the stack (keeps volumes)             |
| `docker compose down -v`                        | Stop the stack and delete the volumes      |

Changes under `backend/app` are reflected immediately through the mounted
source and uvicorn's reloader. Adding or changing dependencies requires a
rebuild:

```bash
docker compose build backend
```

Supporting services expose their default ports on the host: PostgreSQL
`5432`, Redis `6379`, and Qdrant REST `6333` / gRPC `6334`. Inside the
Docker network the backend reaches them by service name (for example
`postgres:5432`), so connection strings in `backend/.env` must use the
service names once the database layer is implemented.

## Docker Production

A production-oriented Docker setup is included. It reuses the same root
`Dockerfile` and `.dockerignore` as development but builds the minimal
`runtime` stage and runs a separate Compose stack.

### Files

- `Dockerfile` (repository root) - the multi-stage image. The `runtime`
  stage installs only the locked runtime dependencies (`uv sync --frozen
  --no-dev`), copies the compiled virtual environment and the application
  source, runs uvicorn (no hot reload) as a non-root user, and registers a
  Docker `HEALTHCHECK` against `/api/v1/health`.
- `docker/production/docker-compose.yml` - the production stack:
  `backend`, `postgres`, `redis`, and `qdrant` on a dedicated `twib-prod`
  bridge network with named volumes, restart policies, and health checks.
- `.dockerignore` (repository root) - shared with the development build;
  keeps the build context limited to the backend subtree.

### Prerequisites

- Docker 24+ with BuildKit (the `syntax=docker/dockerfile:1` directive
  requires it)
- Docker Compose 2+

The backend reads its configuration from `backend/.env` through the
existing settings system. In production, set `APP_ENV=production` and the
infrastructure connection strings there:

```bash
cd backend
cp .env.example .env
```

The production stack overrides `HOST`/`PORT` and forces `APP_ENV=production`
(JSON logging) even if the local `.env` still says `development`.

### Building the Production Image

Build the minimal production image directly:

```bash
docker build --target runtime -t twib-backend:production ../..
```

The `runtime` stage is intentionally small: only the compiled virtual
environment and the application source are copied into it, and it runs as
the non-root `twib` user. Runtime dependencies are pinned through
`uv.lock` (`--frozen`), so installs are reproducible.

### Running the Production Stack

```bash
cd docker/production
docker compose up -d
```

This builds the `runtime` backend image, starts all four services with
`restart: unless-stopped`, and gates backend startup on healthy supporting
services. The API is available at
<http://localhost:8000/api/v1/health>.

To rebuild after an application change:

```bash
docker compose build backend
docker compose up -d
```

To stop the stack:

```bash
docker compose down
```

Named volumes keep PostgreSQL, Redis, and Qdrant data across restarts. To
stop the stack and remove the data volumes too:

```bash
docker compose down -v
```

### Production Notes

- Only the backend publishes a port (`8000:8000`). Supporting services are
  reachable only inside the `twib-prod` network and are not exposed on the
  host.
- The backend container runs as the non-root `twib` user with no source
  bind mounts; deploy by rebuilding the image.
- The Docker `HEALTHCHECK` (image-level) and the compose health checks
  report against `/api/v1/health` and the native readiness probes of the
  supporting services.
- The image uses a single uvicorn worker. Scale out by increasing
  `--workers` (or replicas) once the workload requires it.
- No reverse proxy, orchestration, or cloud deployment is included in this
  phase.

### Difference between Development and Production

| Aspect                 | Development                               | Production                          |
| ---------------------- | ----------------------------------------- | ----------------------------------- |
| Dockerfile stage       | `development` (default)                   | `runtime` (`build.target: runtime`) |
| Dependencies           | All groups (`uv sync --all-groups`)       | Runtime only (`uv sync --frozen --no-dev`) |
| Hot reload             | Yes (`--reload`, bind mounts)             | No (image contains the source)      |
| Source access          | Bind-mounted from the host                | Copied into the image               |
| Docker HEALTHCHECK     | Compose-level health check                | Image `HEALTHCHECK` plus compose health checks |
| Compose file           | `docker/development/docker-compose.yml`   | `docker/production/docker-compose.yml` |
| Compose project name   | `twib`                                    | `twib-prod`                         |
| Network                | `twib-dev` (bridge)                       | `twib-prod` (bridge)                |
| Restart policy         | `unless-stopped` (supporting services)    | `unless-stopped` (all services)     |
| Published ports        | Backend `8000`; postgres `5432`, redis `6379`, qdrant `6333`/`6334` | Backend `8000` only |
| `APP_ENV`              | `development` (from `.env`)               | `production` (forced)               |
| Log format             | Colorized console                         | JSON lines                          |

## Code Quality

The backend is guarded by a code quality toolchain that runs locally and
through Git pre-commit hooks. Every tool is configured centrally in
`pyproject.toml`; there is no separate `.ruff.toml`, `.mypy.ini`, or Black
configuration. The formatter is Ruff; Black is intentionally not used.

Available commands (run from the `backend/` directory):

| Command                   | Purpose                                                  |
| ------------------------- | -------------------------------------------------------- |
| `uv run ruff check .`     | Lint the codebase                                        |
| `uv run ruff format .`    | Apply the Ruff formatter                                  |
| `uv run ruff format --check .` | Verify formatting without modifying files           |
| `uv run mypy app`         | Run strict type checking                                  |

### Linting

Ruff lints the whole package. The enabled rule set covers:

- `E`/`W` - pycodestyle errors and warnings.
- `F` - Pyflakes (unused imports, undefined names).
- `I` - isort import sorting.
- `UP` - pyupgrade modernizations for Python 3.12.
- `B` - flake8-bugbear.
- `SIM` - flake8-simplify.
- `C4` - flake8-comprehensions.
- `RUF` - Ruff-specific rules.
- `ASYNC` - flake8-async (async exception handlers that legitimately await
  nothing are exempted).
- `S` - bandit security rules.
- `A` - flake8-builtins (builtin shadowing).

The exact selection and the two exemptions (`ASYNC220`, `UP040`) are defined
in `[tool.ruff.lint]` in `pyproject.toml`.

### Formatting

Ruff is the only formatter. It targets Python 3.12 with a line length of 88
and double quotes. Run `uv run ruff format .` to apply it and
`uv run ruff format --check .` to verify without modifying files.

### Import Sorting

Import sorting is handled by Ruff's `I` rule set. `app` is registered as a
first-party package (`known-first-party`), so application imports always
sort after standard-library and third-party imports.

### Type Checking

MyPy runs in strict mode (`[tool.mypy]` in `pyproject.toml`) targeting
Python 3.12. Strict mode enables the full family of checks, including
`disallow_untyped_defs`, `disallow_any_generics`, `warn_return_any`, and
`warn_unused_ignores`. FastAPI, Pydantic, structlog, and dependency-injector
all ship type annotations, so no `ignore_missing_imports` overrides are
needed.

### Pre-commit

Git hooks are defined in `.pre-commit-config.yaml` at the repository root.
The hooks run Ruff lint, Ruff format, and MyPy strict on staged backend
files.

```bash
cd backend
uv sync
uv run pre-commit install
```

From then on every commit runs the hooks. To run them manually:

```bash
uv run pre-commit run --all-files
```

### Developer Workflow

1. Make your changes in `backend/app/`.
2. Run `uv run ruff format .` to format.
3. Run `uv run ruff check .` to lint; auto-fixable issues are fixed by the
   pre-commit hook.
4. Run `uv run mypy app` to type check.
5. Stage the files and commit. Pre-commit re-runs Ruff lint, Ruff format,
   and MyPy on the staged backend files and blocks the commit until all
   three pass.

## Testing

The backend is tested with [pytest](https://docs.pytest.org/). The suite
lives in `backend/tests/` and currently covers the HTTP layer through a
reusable FastAPI `TestClient` backed by
[httpx](https://www.python-httpx.org/).

Test dependencies (`pytest`, `pytest-asyncio`, `pytest-cov`, `httpx`) are
part of the `dev` dependency group and are installed by `uv sync`. Pytest
is configured centrally in `backend/pytest.ini` (discovery, coverage, and
async support).

### Test Structure

```text
backend/tests/
├── __init__.py      # Marks the directory as a package
├── conftest.py      # Shared fixtures (reusable TestClient)
└── test_health.py   # Health endpoint tests
```

- `conftest.py` defines the `client` fixture. It builds the application
  through `create_application()` and enters the `TestClient` as a context
  manager so the FastAPI lifespan runs for every test. New test modules
  request the `client` fixture instead of constructing their own client,
  which avoids duplicate setup.
- `test_health.py` verifies `GET /api/v1/health`: the HTTP status code, the
  body against the shared `HealthResponse` schema, the JSON content type,
  and that the application starts and stops cleanly through the lifespan.

### Running Tests

```bash
cd backend
uv run pytest
```

Pytest discovers tests in the `backend/tests/` package (`testpaths` in
`pytest.ini`) and runs them in strict asyncio mode (`asyncio_mode =
strict`), so future async tests opt in with `@pytest.mark.asyncio`.

### Coverage

Coverage is collected by pytest-cov on every run. The `app` package is the
coverage source and the terminal summary is printed by default:

```bash
cd backend
uv run pytest
```

This is the default invocation; `pytest.ini` adds
`--cov=app --cov-report=term-missing` to `addopts`. To inspect coverage in
more detail:

```bash
cd backend
uv run pytest --cov-report=html
```

An HTML report is written to `backend/htmlcov/` (git-ignored).

Only the HTTP infrastructure is tested in this phase. Authentication,
database, repository, service, agent, LLM, and workflow-engine tests are
deferred until those subsystems exist.

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
- Middleware is registered once in `create_application()` through
  `register_middlewares()`. Every request receives a `UUID4` request ID,
  security headers are applied to every response, CORS reads origins from
  settings, and a `RequestContext` is built and exposed on
  `request.state.context`.
- Observability defines the request context object (`RequestContext`), the
  event names, and the metrics and tracing interfaces in
  `app/observability/`. No metrics or tracing backend is implemented in
  this phase; adapters will be added in later phases.
- The domain layer in `app/domain/` defines the framework-independent base
  classes (`Entity`, `AggregateRoot`, `ValueObject`, `DomainEvent`,
  `Identity`) and the domain exception hierarchy (`DomainException`,
  `BusinessRuleViolation`, `EntityNotFound`, `InvalidOperation`,
  `InvalidValue`). It depends only on the Python standard library and is
  consumed by outer layers (services, repositories, API) in later phases.
- The concrete value objects in `app/domain/value_objects/` (identities,
  emails, names, slugs, timestamps, URLs, versions, money, and metadata) are
  immutable, validate their value at construction, and compare by value. They
  are imported from `app.domain.value_objects` and raise `InvalidValue` on
  invalid input; no serialization or framework code lives here.
- The user domain in `app/domain/users/` models the `User` aggregate root
  (built from the value objects, with `UserStatus`/`UserRole` enums, user
  domain events, and user business-rule exceptions). State is exposed only
  through read-only properties; domain methods validate, record events, and
  auto-bump the optimistic-locking version. No authentication, password,
  database, repository, or API code exists in the domain layer.
- Logging, dependency injection, exception handling, middleware, the API
  foundation (schemas, tags, response helpers, OpenAPI metadata), and the
  observability foundation (request context, event definitions, metrics and
  tracing interfaces) are the cross-cutting infrastructure implemented so
  far. Authentication, database, and business endpoints are intentionally
  deferred to later phases.
- Follow the project coding guidelines (PEP 8, type hints, Google-style
  docstrings). Do not add code outside the current phase.
