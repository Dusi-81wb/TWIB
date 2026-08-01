# TWIB Technology Stack

## Overview

This document details the chosen technologies for TWIB and explains WHY each was selected. Every technology choice supports the architectural principles of Clean Architecture, loose coupling, and replaceability.

---

## Frontend

### Next.js 14+ (App Router)

**Selected**: Next.js 14+ with App Router, React Server Components

**Why**:
- **Server Components**: Reduce client-side JavaScript, improving initial load performance and SEO
- **App Router**: Nested layouts, route groups, parallel routes, and streaming - ideal for complex dashboard apps
- **API Routes**: Integrated backend capability for server-side proxy and BFF pattern
- **Incremental Static Regeneration (ISR)**: Perfect for template pages and public content
- **TypeScript First**: First-class TypeScript support
- **Vercel Ecosystem**: Seamless deployment, preview environments
- **Middleware**: Edge-level routing, auth, and A/B testing

**Alternatives Considered**: React SPA (Create React App), Vue/Nuxt, SvelteKit
- Rejected: SPA lacks SSR/SEO and streaming; Vue/Svelte have smaller ecosystems for enterprise

### TypeScript 5+

**Selected**: TypeScript 5+ strict mode

**Why**:
- **Type Safety**: Catches errors at compile time, reduces production bugs
- **Shared Types**: API contracts can be generated from OpenAPI to TS types
- **Developer Experience**: Excellent IDE support, autocomplete, refactoring
- **Enterprise Standard**: Industry default for large frontend codebases

### Zustand + TanStack Query

**Selected**: Zustand for client state, TanStack Query for server state

**Why**:
- **TanStack Query**: Handles caching, retries, pagination, optimistic updates for server data; eliminates boilerplate
- **Zustand**: Lightweight (~1KB), minimal boilerplate, no provider nesting, great for UI/global state
- **Separation of Concerns**: Server state ≠ client state, different tools
- **Alternatives**: Redux (boilerplate-heavy), Recoil/Jotai (less mature)

### Radix UI + Tailwind CSS

**Selected**: Radix UI primitives + Tailwind CSS

**Why**:
- **Radix UI**: Unstyled, accessible, composable primitives - full design control
- **Tailwind CSS**: Utility-first, design tokens, dark mode, consistent spacing
- **Radix + Tailwind**: Accessible components with custom styling, no CSS framework lock-in
- **Alternatives**: MUI (opinionated, heavier), Ant Design (heavy), Chakra (less flexible)

### Socket.io Client

**Selected**: Socket.io for real-time client communication

**Why**:
- **Auto-Reconnect**: Handles network instability
- **Rooms/Namespaces**: Perfect for workflow rooms, org channels
- **Fallback**: WebSocket → HTTP long-polling fallback
- **Cross-provider**: Works with any Socket.io server

### React Hook Form + Zod

**Selected**: React Hook Form + Zod schema validation

**Why**:
- **Performance**: Minimizes re-renders
- **Zod**: Type-safe, shared schema with backend (Pydantic-like for TS)
- **Controller Pattern**: Works well with Radix UI components

---

## Backend

### Python 3.11+

**Selected**: Python 3.11+ as the backend language

**Why**:
- **AI/ML Ecosystem**: First-class support for LLM SDKs (OpenAI, Anthropic), ML libraries
- **Async Support**: Native `asyncio`, `async/await` for high concurrency
- **Type Hints**: Mature type system, mypy/pyright
- **Fast Development**: Rapid iteration for complex business logic
- **Team Productivity**: Readable, maintainable, widely understood

### FastAPI

**Selected**: FastAPI as the web framework

**Why**:
- **Async Native**: Full asyncio support for concurrent LLM calls, database operations
- **Pydantic v2 Integration**: Automatic request/response validation, serialization
- **OpenAPI/Swagger**: Auto-generated documentation, client SDK generation
- **Performance**: Comparable to Node.js/Go for I/O-bound workloads
- **Dependency Injection**: Native `Depends()` pattern, testability
- **WebSocket Support**: First-class WebSocket for real-time features

**Alternatives Considered**: Django (monolithic, sync-first), Flask (no async, less structure), Litestar/Starlette (less ecosystem)

### Pydantic v2

**Selected**: Pydantic v2 for data validation

**Why**:
- **Speed**: Rust core, 5-50x faster than v1
- **Strict Validation**: Enforce types, constraints
- **Settings Management**: Pydantic Settings for config
- **Serialization**: `model_dump()`, `model_validate()` for clean DTOs

### dependency-injector

**Selected**: dependency-injector for DI container

**Why**:
- **Declarative**: Clean container definition
- **Scopes**: Singleton, Factory, Request scopes
- **Override**: Test overrides for mocking
- **Protocol Support**: Register by interface
- **Mature**: Production-proven

**Alternatives**: FastAPI Depends (limited for complex graphs), di, punq

### PostgreSQL + SQLAlchemy 2.0

**Selected**: PostgreSQL 15+ with SQLAlchemy 2.0 async

**Why**:
- **PostgreSQL**: ACID, JSONB, full-text search, mature, managed services available
- **SQLAlchemy 2.0**: Async support, typing, modern ORM
- **Repository Pattern**: Abstraction allows swapping ORM if needed
- **Alternatives**: MySQL (weaker JSON/full-text), SQLite (not production), raw SQL (no ORM benefits)

### Alembic

**Selected**: Alembic for database migrations

**Why**:
- **SQLAlchemy Integration**: Native, autogenerate from models
- **Versioned**: Downgrade/upgrade paths
- **Industry Standard**: Documented, tested, widely used

---

## Data Layer

### Redis / Valkey 7+

**Selected**: Redis/Valkey for caching, pub/sub, streams

**Why**:
- **Performance**: Sub-millisecond latency
- **Data Structures**: Strings, hashes, lists, sorted sets for flexible caching
- **Pub/Sub**: Real-time event fan-out
- **Streams**: Durable message queue for async processing (replaces Kafka for MVP)
- **Lua Scripts**: Atomic operations
- **Redis Adapter**: Socket.io and Celery integration

**Alternatives**: Memcached (no pub/sub/streams), Kafka (heavier, needed later)

### Qdrant

**Selected**: Qdrant for vector database

**Why**:
- **Purpose-Built**: Optimized for vector similarity search
- **Filtering**: Filters combined with vector search (metadata + semantic)
- **Performance**: HNSW index, fast queries
- **Docker/K8s**: Easy deployment, horizontal scaling
- **Client SDK**: Python client, typed

**Alternatives**: Pinecone (managed, vendor lock-in, costly), Weaviate (heavier), Milvus (complex ops), pgvector (limits at scale)

### S3 / GCS / Azure Blob

**Selected**: Multi-cloud object storage

**Why**:
- **Durability**: 11 nines
- **Scalability**: Infinite, elastic
- **CDN**: Global distribution
- **Presigned URLs**: Secure uploads/downloads
- **Multi-provider**: Avoid lock-in (via storage abstraction)

---

## LLM / AI

### Multi-Provider Strategy

**Selected**: OpenAI, Anthropic, Ollama, Azure, Bedrock, Vertex

**Why**:
- **Avoid Lock-in**: Provider abstraction (Clean Architecture) makes swapping trivial
- **Cost Optimization**: Route to cheapest capable model
- **Reliability**: Fallback when one provider fails
- **Best Model for Task**: Different providers excel at different tasks

### OpenAI
- GPT-4o, GPT-4o-mini, GPT-3.5 Turbo
- text-embedding-3-large/small
- Best-in-class general reasoning, function calling

### Anthropic
- Claude 3 Opus, Sonnet, Haiku
- Long context (200K), nuanced reasoning
- Strong for complex agent chains

### Ollama (Local)
- Llama 3, Mistral, etc.
- On-prem, data privacy, offline
- Cost-free for development/testing

### HuggingFace / Sentence Transformers
- Local embeddings option
- Data sovereignty, offline

---

## Authentication

### Auth0 / Clerk

**Selected**: Auth0 (or Clerk) for managed identity

**Why**:
- **Security**: Battle-tested, SOC 2, zero self-implemented crypto
- **SSO**: Enterprise SAML/OIDC/Google/GitHub
- **MFA**: Built-in, including TOTP/WebAuthn
- **RBAC**: Roles, permissions, org management
- **Compliance**: SOC 2, GDPR, HIPAA-ready
- **SDK**: Clean integration with FastAPI/Next.js

**Alternatives**: Custom JWT (risk, time), Keycloak (ops burden), AWS Cognito (SDK friction)

---

## Payments

### Stripe

**Selected**: Stripe for payments/billing

**Why**:
- **Billing**: Subscriptions, metered billing, usage-based pricing
- **Customer Portal**: Self-service (no custom UI needed)
- **Webhooks**: Reliable event delivery
- **Tax**: Stripe Tax for automated tax calculation
- **Global**: Multi-currency, international
- **SDK**: Mature Python SDK

---

## Real-time

### Socket.io (Python: python-socketio)

**Selected**: Socket.io for WebSocket real-time

**Why**:
- **Rooms/Namespaces**: Perfect for org/room-scoped events
- **Reconnection**: Auto-reconnect, buffered events
- **Redis Adapter**: Horizontal scaling
- **Fallback**: HTTP long-polling fallback
- **Ecosystem**: Same protocol as frontend client

---

## Observability

### Prometheus + Grafana

**Selected**: Prometheus (metrics) + Grafana (dashboards)

**Why**:
- **Standard**: Industry standard, huge ecosystem
- **Custom Metrics**: Instrument business metrics (LLM cost, executions)
- **Alerting**: Built-in alert manager
- **Self-hosted**: No vendor lock-in, can migrate to managed (Grafana Cloud, Datadog)

### OpenTelemetry + Jaeger

**Selected**: OpenTelemetry for tracing, Jaeger for visualization

**Why**:
- **OpenStandard**: Vendor-neutral instrumentation
- **Distributed Tracing**: Track LLM calls, workflow executions across services
- **Correlation**: Trace IDs tie logs/metrics/traces

### structlog + JSON Logging

**Selected**: structlog for structured logging

**Why**:
- **Key-Value**: Machine-parseable logs
- **Correlation IDs**: Auto-context binding
- **JSON Output**: Compatible with Loki, Elasticsearch, CloudWatch

---

## Testing

### pytest + pytest-asyncio

**Selected**: pytest as the testing framework

**Why**:
- **Standard**: Industry standard for Python
- **Fixtures**: Powerful fixture system
- **Async**: pytest-asyncio for async tests
- **Plugins**: cov, xdist (parallel), timeout, mock

### httpx (Async TestClient)

**Selected**: httpx for API testing

**Why**:
- **Async**: Native async test client for FastAPI
- **Realistic**: Actual HTTP transport (mocking optional)
- **Resilient**: Retries, timeouts built-in

### factory-boy + faker

**Selected**: factory-boy for test data, faker for realistic data

**Why**:
- **Fixtures**: Avoid brittle fixture code
- **Reproducibility**: Deterministic factories
- **Realism**: faker generates realistic names/emails/dates

---

## Frontend Testing

### Vitest + React Testing Library + Playwright

**Selected**:

**Vitest**: Fast, Vite-native unit test runner
- ESModule-first, TypeScript out-of-box

**React Testing Library**: Component testing
- Encourages user-centric tests

**Playwright**: E2E testing
- Cross-browser, reliable, auto-wait
- Test workflow builder drag-drop, execution flows

---

## DevOps & CI/CD

### GitHub Actions

**Selected**: GitHub Actions for CI/CD

**Why**:
- **Native**: GitHub integration (PRs, branches)
- **Matrix Builds**: Test multiple Python/Node versions
- **Marketplace**: Reusable actions
- **Self-hosted**: Run on own runners for speed
- **No cost**: Included with GitHub

### Docker + Docker Compose

**Selected**: Docker for containerization

**Why**:
- **Reproducibility**: Identical dev/prod environments
- **Microservices**: Each service containerized
- **Compose**: Local orchestration (backend, frontend, Postgres, Redis, Qdrant)

### Kubernetes (EKS/GKE) + Helm

**Selected**: Kubernetes + Helm for production orchestration

**Why**:
- **Scaling**: Horizontal auto-scaling (HPA)
- **Self-healing**: Restart failed pods
- **Helm**: Parameterized deployments per environment
- **Ecosystem**: Prometheus, Ingress, Secrets integration

### Terraform

**Selected**: Terraform for infrastructure-as-code

**Why**:
- **Reproducible**: Infrastructure in code
- **Multi-cloud**: AWS, GCP, Azure
- **State**: Tracked, auditable
- **Reviewable**: PRs for infrastructure changes

---

## Package Management

### Backend: uv / Poetry

**Selected**: uv (or Poetry) for Python packaging

**Why**:
- **uv**: Extremely fast dependency resolution/installation
- **Lockfile**: Reproducible builds
- **pyproject.toml**: Standard Python packaging
- **Environment**: `.venv` management

### Frontend: npm/pnpm

**Selected**: npm (or pnpm) for Node packages

**Why**:
- **pnpm**: Faster, disk-efficient, strict deps
- **Lockfile**: Reproducible installs

---

## Shared / Codegen

### OpenAPI Codegen

**Selected**: OpenAPI + code generation for shared types

**Why**:
- **Single Source of Truth**: Backend schemas → OpenAPI → TS types
- **Type Safety**: Frontend/backend contracts never drift
- **Tooling**: `openapi-typescript` or `orval` for TS client generation

---

## Summary Table

| Layer | Technology | Why |
|-------|------------|-----|
| Frontend | Next.js 14+, TS, Tailwind, Radix, Zustand, TanStack Query | SSR, type safety, accessible, fast |
| Backend | FastAPI, Pydantic v2, Python 3.11 | Async, validation, OpenAPI |
| DI | dependency-injector | Declarative, testable |
| Database | PostgreSQL + SQLAlchemy 2.0 | ACID, async, JSONB |
| Migrations | Alembic | Native SQLAlchemy |
| Cache/Queue | Redis/Valkey | Fast, pub/sub, streams |
| Vector DB | Qdrant | Purpose-built, filtered search |
| Storage | S3/GCS/Azure | Durable, scalable |
| LLM | OpenAI, Anthropic, Ollama | Multi-provider, cost-optimized |
| Auth | Auth0/Clerk | Security, SSO, MFA, RBAC |
| Payments | Stripe | Billing, subscriptions, usage |
| Real-time | Socket.io + Redis | Rooms, reconnect, scaling |
| Metrics | Prometheus + Grafana | Standard, custom metrics |
| Tracing | OpenTelemetry + Jaeger | Distributed tracing |
| Logging | structlog + JSON | Structured, correlation |
| Testing | pytest, httpx, factory-boy | Async, realistic, deterministic |
| Frontend Test | Vitest, RTL, Playwright | Unit, component, E2E |
| CI/CD | GitHub Actions | Native, matrix |
| Orchestration | K8s + Helm | Scaling, self-healing |
| Infra-as-Code | Terraform | Reproducible, multi-cloud |
| Python Pkg | uv/Poetry | Fast, lockfile |
| Node Pkg | npm/pnpm | Fast, strict |

---

## Technology Decision Principles

Every technology was chosen based on:

1. **Enterprise Readiness**: Production-proven, active maintenance, security track record
2. **Replaceability**: Abstracted behind interfaces; each can be swapped without touching business logic
3. **Ecosystem**: Strong community, documentation, hiring pool
4. **Performance**: Meets or exceeds platform requirements (sub-ms cache, low-latency API)
5. **Cost-Efficiency**: Optimize cost, especially LLM usage (routing, caching)
6. **Developer Experience**: Reduces boilerplate, speeds development
7. **Scalability**: Horizontal scaling capability from day one