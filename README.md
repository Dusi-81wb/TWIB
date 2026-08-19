# TWIB - Total Workflow Intelligence Builder

## Project Overview

TWIB (Total Workflow Intelligence Builder) is an enterprise-grade AI SaaS platform that generates intelligent business workflows using multiple specialized AI agents. The platform enables organizations to automate complex business processes through AI-driven workflow orchestration, combining the power of large language models with structured workflow execution.

### Vision

To become the premier platform for AI-powered business workflow automation, enabling enterprises to design, deploy, and manage intelligent workflows that adapt and optimize themselves over time.

### Mission

Deliver a production-ready, modular, scalable, and maintainable architecture that serves as the foundation for all future development. Every architectural decision must prioritize:
- **Replaceability**: Every module can be swapped without affecting others
- **Loose Coupling**: Modules communicate through well-defined interfaces
- **Single Responsibility**: Each module has one clear purpose
- **Testability**: All components are independently testable
- **Extensibility**: New capabilities can be added without modifying core code

---

## Architecture

TWIB follows **Clean Architecture** with strict layer separation:

```
Presentation Layer (Frontend)
        ↓
API Layer (REST/WebSocket)
        ↓
Service Layer (Business Logic)
        ↓
Domain Layer (Entities, Value Objects, Domain Events)
        ↓
Repository Layer (Data Access Abstractions)
        ↓
Infrastructure Layer (External Systems, Databases, LLM Providers)
```

### Core Principles

| Principle | Implementation |
|-----------|----------------|
| **Dependency Rule** | Inner layers never depend on outer layers |
| **Dependency Injection** | All dependencies provided via constructor injection |
| **Repository Pattern** | Data access abstracted behind interfaces |
| **Service Pattern** | Business logic encapsulated in services |
| **SOLID** | All code follows SOLID principles |
| **DRY/KISS** | No duplication, simple solutions preferred |

### Module Boundaries

- **Business Logic**: ONLY in Service Layer
- **Data Access**: ONLY in Repository Layer
- **External Communication**: ONLY in Infrastructure Layer
- **API Contracts**: Defined in Schemas
- **Cross-cutting Concerns**: Middleware, Exceptions, Utils

---

## Folder Structure

```
TWIB/
├── frontend/                 # Next.js React application
├── backend/                  # FastAPI Python application
│   ├── api/                  # Route definitions (thin)
│   ├── middleware/           # Cross-cutting concerns
│   ├── dependencies/         # DI container & providers
│   ├── config/               # Configuration management
│   ├── websocket/            # Real-time communication
│   ├── services/             # Business logic (core)
│   ├── schemas/              # Pydantic models (API contracts)
│   ├── exceptions/           # Custom exception hierarchy
│   ├── utils/                # Pure utility functions
│   └── core/                 # Application bootstrap
├── agents/                   # AI Agent implementations
│   ├── planner/              # Task planning & decomposition
│   ├── analyst/              # Requirements analysis
│   ├── architect/            # Solution architecture
│   ├── validator/            # Output validation
│   ├── optimizer/            # Workflow optimization
│   ├── researcher/           # Information gathering
│   ├── documentation/        # Auto-documentation
│   └── supervisor/           # Multi-agent orchestration
├── workflows/                # Workflow engine
│   ├── graph/                # Graph data structures
│   ├── nodes/                # Node types & definitions
│   ├── edges/                # Edge types & routing
│   ├── templates/            # Pre-built workflow templates
│   ├── executor/             # Execution engine
│   └── memory/               # Workflow state & memory
├── llm/                      # LLM abstraction layer
│   ├── providers/            # Provider implementations
│   ├── router/               # Model routing logic
│   ├── embeddings/           # Embedding generation
│   ├── tokenizer/            # Token management
│   └── context/              # Context window management
├── auth/                     # Authentication & authorization
├── database/                 # Database layer
│   ├── models/               # ORM models
│   ├── repositories/         # Repository implementations
│   ├── migrations/           # Schema migrations
│   └── seed/                 # Seed data
├── vector_db/                # Vector database integration
├── cache/                    # Caching layer
├── payments/                 # Payment processing
├── realtime/                 # Real-time features
├── analytics/                # Analytics & monitoring
├── security/                 # Security utilities
├── storage/                  # File storage abstraction
├── docker/                   # Docker configurations
├── deployment/               # Deployment scripts
├── tests/                    # Test suite
└── docs/                     # Documentation
```

---

## 🚀 Quick Start

### Prerequisites
* **Python**: 3.12 or higher
* **Node.js**: 18.x or 20.x (with npm)
* **Docker & Docker Compose** (optional, for full containerized stack)

---

### Option A: Local Development Setup

#### 1. Clone the repository
```bash
git clone https://github.com/Dusi-81wb/TWIB.git
cd TWIB
```

#### 2. Backend Setup (FastAPI)
```bash
cd backend

# Create and activate Python virtual environment
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies (Standard pip)
pip install -r requirements.txt

# Or using uv (Fast package manager)
# uv sync

# Configure environment variables
cp .env.example .env

# Run FastAPI Server
uvicorn app.main:app --reload --port 8000
```
* **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

#### 3. Frontend Setup (Next.js 15)
In a new terminal window:
```bash
cd frontend

# Install Node dependencies
npm install

# Configure environment variables
cp .env.example .env.local

# Run Next.js Dev Server
npm run dev
```
* **Web Application**: [http://localhost:3000](http://localhost:3000)

---

### Option B: Docker Compose Setup

Run the entire platform (Backend, Frontend, PostgreSQL, Redis, Qdrant) with a single command:
```bash
docker compose -f docker/development/docker-compose.yml up --build
```

---

## Technology Stack


### Backend
| Component | Technology | Rationale |
|-----------|------------|-----------|
| Framework | **FastAPI** | High performance, async native, automatic OpenAPI docs, type-safe |
| Language | **Python 3.11+** | Rich AI/ML ecosystem, excellent async support, type hints |
| DI Container | **dependency-injector** | Mature, declarative, supports scopes |
| Validation | **Pydantic v2** | Fast, strict, integrates with FastAPI |
| Database | **PostgreSQL + SQLAlchemy 2.0** | ACID, mature, async support, JSONB |
| Migrations | **Alembic** | Standard for SQLAlchemy |
| Vector DB | **Qdrant** | Purpose-built, filtered search, scalable |
| Cache | **Redis (Valkey)** | Sub-ms latency, pub/sub, streams |
| Message Queue | **Redis Streams** | Built-in, no extra infrastructure |
| Auth | **Auth0 / Clerk** | Enterprise SSO, MFA, compliance |
| LLM Providers | **OpenAI, Anthropic, Ollama** | Multi-provider strategy, cost optimization |

### Frontend
| Component | Technology | Rationale |
|-----------|------------|-----------|
| Framework | **Next.js 14+ (App Router)** | React Server Components, streaming, SEO |
| Language | **TypeScript 5+** | Type safety, excellent DX |
| State | **Zustand + TanStack Query** | Lightweight, server state separation |
| UI | **Radix UI + Tailwind CSS** | Accessible primitives, utility-first |
| Real-time | **Socket.io Client** | Auto-reconnect, rooms, fallback |
| Forms | **React Hook Form + Zod** | Performant, schema validation |

### DevOps & Infrastructure
| Component | Technology | Rationale |
|-----------|------------|-----------|
| Containerization | **Docker + Docker Compose** | Standard, reproducible |
| Orchestration | **Kubernetes (EKS/GKE)** | Auto-scaling, self-healing |
| CI/CD | **GitHub Actions** | Native integration, matrix builds |
| Monitoring | **Prometheus + Grafana** | Industry standard, custom metrics |
| Logging | **Structured JSON + Loki** | Queryable, correlated |
| Tracing | **OpenTelemetry + Jaeger** | Distributed tracing |
| Secrets | **HashiCorp Vault / AWS Secrets Manager** | Secure, auditable |

---

## Coding Standards

### Naming Conventions
| Element | Convention | Example |
|---------|------------|---------|
| Directories | `snake_case` | `user_management` |
| Files | `snake_case.py` | `user_service.py` |
| Classes | `PascalCase` | `UserService` |
| Functions/Methods | `snake_case` | `get_user_by_id` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRY_ATTEMPTS` |
| Type Variables | `PascalCase` with `T` prefix | `TUser` |
| Private | `_leading_underscore` | `_internal_method` |

### Async Conventions
- All I/O operations MUST be async
- Use `async def` for all service methods
- Never block event loop (no `time.sleep`, use `asyncio.sleep`)
- Use `async with` for context managers
- Prefer `asyncio.gather` for concurrent operations

### Error Handling
- Custom exceptions in `backend/exceptions/`
- Never catch bare `Exception`
- Use exception chaining (`raise ... from ...`)
- Log at appropriate level (error/warning/info)
- Return typed error responses via schemas

### Dependency Injection
- All services registered in `backend/dependencies/`
- Use protocol/interfaces for contracts
- Constructor injection only
- Scopes: singleton (stateless), request (stateful)

### Repository Pattern
- Abstract base class in `database/repositories/base.py`
- One repository per aggregate root
- Methods return domain entities, not ORM models
- No business logic in repositories

### Service Pattern
- One service per business capability
- Stateless, singleton-scoped
- Coordinate repositories, not entities
- Emit domain events for side effects

### Type Hints
- **Mandatory** on all public APIs
- Use `typing` module imports
- Prefer `Protocol` over `ABC` for contracts
- Annotate return types always

### Docstrings
- Google style docstrings
- Required for all public classes/methods
- Include args, returns, raises, example

### Imports
- Standard library first
- Third-party second
- Local third
- Absolute imports only
- No wildcard imports

---

## Development Workflow

### Branching Strategy
```
main (protected)
  └── develop (integration)
        ├── feature/* (new features)
        ├── fix/* (bug fixes)
        ├── docs/* (documentation)
        └── refactor/* (code improvements)
```

### Commit Convention (Conventional Commits)
```
<type>(<scope>): <subject>

<body>

<footer>
```
Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`

### Pull Request Process
1. Create feature branch from `develop`
2. Implement with tests
3. Run lint, typecheck, tests locally
4. Open PR with description linking issue
5. Code review (min 1 approval)
6. CI passes (lint, typecheck, tests, build)
7. Squash merge to `develop`

### Release Process
1. Create `release/vX.Y.Z` from `develop`
2. Version bump, changelog update
3. Deploy to staging
4. Integration tests on staging
5. Merge to `main` with tag
6. Deploy to production

---

## Roadmap

### Phase 0: Architecture ✅ **COMPLETE**
- [x] Folder structure
- [x] Documentation (architecture.md, folder_structure.md, coding_guidelines.md, development_workflow.md, TECH_STACK.md)
- [x] Coding standards (Ruff, MyPy strict, pre-commit)
- [x] Tech stack decisions (FastAPI, Next.js 15, PostgreSQL, SQLAlchemy 2.0, Redis, Qdrant, JWT/OAuth2, Docker/K8s)

### Phase 1: Foundation ✅ **COMPLETE**
- [x] Project bootstrap (pyproject.toml, uv lockfile, dependency groups)
- [x] Configuration system (Pydantic Settings v2, environment-based, validation)
- [x] Logging infrastructure (structlog, JSON/production, console/dev, correlation IDs)
- [x] Exception hierarchy (TWIBException + 6 generic exceptions, error codes, global handlers)
- [x] DI container (dependency-injector, ApplicationContainer, singleton/factory providers)
- [x] FastAPI application factory (lifespan, container on app.state, health endpoint)
- [x] OpenAPI customization (centralized tags, response envelopes, metadata)
- [x] Middleware stack (security headers, request ID, CORS, observability)
- [x] Code quality (Ruff lint/format, MyPy strict, pre-commit hooks)
- [x] Testing infrastructure (pytest, pytest-asyncio, httpx, TestClient fixture, coverage)
- [x] Docker development (multi-stage Dockerfile, docker-compose.yml with postgres/redis/qdrant)
- [x] Docker production (multi-stage runtime target, non-root user, health checks, named volumes)
- [x] Observability foundation (RequestContext, events, metrics/tracing protocols, middleware)
- [x] Foundation review (ADR-0008 backend layout, ADR-0009 hybrid auth, doc sync)

### Phase 2: Domain Layer ✅ **COMPLETE**
- [x] Domain foundation (Entity, AggregateRoot, ValueObject, DomainEvent, Identity, domain exceptions)
- [x] Value objects (UuidIdentity, Email, Name, Slug, Timestamp, Url, Version, Money, Metadata, Description)
- [x] User domain (User aggregate, statuses/roles enums, domain events, business-rule exceptions)
- [x] Organization domain (Organization aggregate, memberships, plans/statuses, events, exceptions)
- [x] Workspace domain (Workspace aggregate, memberships/settings, visibility/roles, events, exceptions)
- [x] Repository interfaces (generic Repository protocol, User/Organization/Workspace repositories, UnitOfWork)

### Phase 3: Database Layer ✅ **COMPLETE**
- [x] SQLAlchemy 2.0 async infrastructure (engine, session factory, declarative base, connection pooling)
- [x] SQLAlchemy models (User, Organization, Membership, Workspace, WorkspaceMembership, WorkspaceSettings)
- [x] Repository implementations (User/Organization/Workspace repositories with full CRUD + queries)
- [x] UnitOfWork implementation (session-bound, transaction boundary, repository access)
- [x] Alembic migrations (initial schema, subsequent migrations for all domain models)
- [x] Seed data (development and testing seeds)

### Phase 4: Authentication ✅ **COMPLETE**
- [x] Hybrid auth (Auth0/Clerk as IdP + TWIB session JWTs + opaque refresh tokens in Redis)
- [x] JWT validation middleware (JWKS caching, RS256, audience/issuer validation)
- [x] Session management (short-lived access tokens, Redis refresh tokens, rotation)
- [x] RBAC (Owner/Admin/Member/Viewer roles at org and workspace level)
- [x] API key management (hashing, scopes, rotation, last-used tracking)
- [x] Auth schemas & routes (login, callback, refresh, logout, me, API keys CRUD)
- [x] Organization/workspace context extraction middleware

### Phase 5: LLM Layer ✅ **COMPLETE**
- [x] Provider abstraction (LLMProvider protocol, Completion/Message/Chunk types, streaming)
- [x] OpenAI provider (GPT-4o, GPT-4o-mini, embeddings, streaming, token counting)
- [x] Ollama provider (local models, streaming, embeddings)
- [x] Provider registry & factory (capability-based selection, health checks)
- [x] Conversation management (history, context window, token budgeting)
- [x] Streaming support (SSE-compatible chunk emission)
- [x] Usage tracking (tokens, cost, latency per request)
- [x] Verification suite (all providers, streaming, embeddings, error handling)

### Phase 6: Model Router ✅ **COMPLETE**
- [x] Routing strategies (cost-aware, latency-aware, capability-based, fallback chains)
- [x] Model registry (capabilities, pricing, limits, availability)
- [x] Per-request routing hints
- [x] Organization-level preferences
- [x] Cost attribution per workflow/agent
- [x] Budget enforcement & alerts

### Phase 7: Agent Framework ✅ **COMPLETE**
- [x] BaseAgent abstract class (execute, validate, lifecycle, context/memory integration)
- [x] Agent protocol definitions (AgentContext, AgentResult, ValidationResult)
- [x] Inter-agent communication (message passing via Supervisor, handoff protocol)
- [x] Agent memory (short-term session, long-term org preferences, semantic/vector, workflow)
- [x] Context Manager (history retrieval, conversation compression, knowledge retrieval, token budgeting)
- [x] Prompt template system (versioned, Jinja2, token optimization)
- [x] **Planner Agent** (goal decomposition, task graph, dependency identification, resource estimation, risk assessment)
- [x] **Analyst Agent** (requirements parsing, constraint extraction, gap analysis, feasibility scoring)
- [x] **Architect Agent** (component design, data flow modeling, integration patterns, technology selection, Mermaid diagrams)
- [x] **Validator Agent** (output validation, code quality, security scanning, performance benchmarking, test generation)
- [x] **Optimizer Agent** (bottleneck detection, cost analysis, parallelization, caching recommendations, model selection)
- [x] **Researcher Agent** (web search, API doc retrieval, best practice synthesis, knowledge caching)
- [x] **Documentation Agent** (technical specs, user guides, API docs, architecture diagrams, multi-format output)
- [x] **Supervisor Agent** (multi-agent orchestration, handoff management, conflict resolution, quality gates, progress tracking, failure recovery, human-in-the-loop escalation)
- [x] Agent registry & execution sandbox (timeout enforcement, result aggregation, event emission)
- [x] Verification suite (all 8 agents, communication, memory, context, sandbox)

### Phase 8: Workflow Engine ✅ **COMPLETE**
- [x] Graph structures (WorkflowGraph DAG, topological sort, cycle detection, subgraph extraction, serialization)
- [x] Node types (LLMNode, ToolNode, ConditionNode, LoopNode, ParallelNode, HumanNode, AgentNode, SubworkflowNode)
- [x] Edge types (SequenceEdge, ConditionEdge, ParallelEdge, ErrorEdge, CompensationEdge for saga rollback)
- [x] WorkflowExecutor (topological + dynamic scheduling, persistent state, checkpointing, recovery, retry policies, timeouts)
- [x] Event emission (started, node_start, node_complete, failed, completed, checkpoint)
- [x] Memory system (variable scoping, semantic/vector memory, checkpoint storage, GC policies, agent querying)
- [x] Template system (registry, parameter validation, versioning, built-in templates: approval, ETL, notification, data_processing)
- [x] Human approval checkpoints (pause/resume, revision loops)
- [x] Verification suite (graph algorithms, node execution, executor integration, recovery, distributed execution)

### Phase 9: REST API & Realtime Layer ✅ **COMPLETE**
- [x] Workflow API (CRUD, execute, executions list, versions, templates instantiate)
- [x] Agent API (list agents, execute single agent, agent history)
- [x] Realtime events (WebSocket server, Socket.io, connection auth, Redis adapter for scaling)
- [x] Workflow monitoring (live execution view, node status, log streaming, error details, retry/cancel)
- [x] Public API & SDK preparation (versioned /api/v1/, consistent envelopes, pagination/filtering/sorting, RFC 7807 errors, rate limiting)
- [x] Verification suite (all endpoints, realtime events, monitoring, SDK types)

### Phase 10: Frontend Architecture & Applications ✅ **COMPLETE**
- [x] Frontend foundation (Next.js 15 App Router, TypeScript, Tailwind CSS, shadcn/ui, TanStack Query, Zustand, Axios with JWT refresh queue)
- [x] Authentication UI (Login, Register, Forgot/Reset Password, ProtectedRoute/GuestRoute, Zod validation)
- [x] Dashboard (responsive layout, sidebar, top nav, workspace selector, user menu, stats cards, activity feed, system health)
- [x] Workflow Builder (form-based `/workflows/new`, template selector, prompt editor, pipeline preview, execution options, live summary)
- [x] Workflow Monitor (real-time `/workflows/[workflowId]`, header status, progress bar, multi-agent timeline, active agent card, WebSocket telemetry)
- [x] Agent Console (`/agents`, core roster selector, agent info card, prompt editor, output viewer, execution history)
- [x] Organization & Workspace Management (org/workspace dashboards, member RBAC table, role selector, email invitations, delete confirmation)
- [x] Settings (`/settings`, 8-tab sidebar: Profile, Account, Appearance, Notifications, AI Providers, API Keys, Security, About)
- [x] Frontend verification (all 8 modules, routing, typing, state, API client integration)

### Phase 11: Production & Deployment 🟢 **IN PROGRESS**
- [ ] Production Docker images (multi-arch, security scanning, SBOM)
- [ ] Kubernetes manifests (namespace strategy, deployments, services, ingress with TLS/WAF, HPA, PDB, network policies)
- [ ] Helm charts (main chart + subcharts, values per env, dependency charts for PG/Redis/Qdrant)
- [ ] CI/CD pipelines (multi-arch build, Trivy/Snyk scanning, integration tests, staging auto-deploy, prod manual approval, blue/green, rollback)
- [ ] Environments (per-PR preview, staging on develop, production on main, DR backup/restore tested)
- [ ] Environment configuration (secrets management, Vault/AWS Secrets Manager, config per env)

### Phase 12: Analytics 📋 **PLANNED**
- [ ] Event pipeline (collector, validation, Redis Streams processing, DLQ, replay)
- [ ] Metrics (RED per endpoint, business KPIs, cost/performance metrics, custom definitions)
- [ ] Dashboards (Grafana system health, business KPIs, agent performance, workflow analytics, cost attribution, user funnels)
- [ ] Reports (scheduled generation, custom builder, CSV/PDF/JSON export, email/webhook delivery)
- [ ] Alerting (threshold/anomaly rules, email/Slack/PagerDuty, grouping/deduplication, silencing, runbook links)

### Phase 13: Production Hardening 📋 **PLANNED**
- [ ] Load testing (k6/Locust, 10x expected traffic)
- [ ] Chaos engineering (Litmus/Chaos Mesh, failure injection, no data loss)
- [ ] Security (pentest, SAST/DAST, secret scanning, RBAC audit, encryption at rest/transit, PII handling, GDPR/CCPA, SOC 2 prep)
- [ ] Observability (OpenTelemetry+Jaeger distributed tracing, Loki log aggregation, custom dashboards, synthetic monitoring, RUM)
- [ ] Operations (backup/restore tested, DB maintenance windows, cert rotation, dependency updates, security patches, on-call, postmortems)
- [ ] Performance (query optimization, caching review, CDN, connection pooling, LLM response caching, cold start optimization)

---

## Current Status Summary

| Layer | Status | Notes |
|-------|--------|-------|
| Architecture | ✅ Complete | Clean Architecture, ADR-0008/0009 locked |
| Domain Layer | ✅ Complete | 3 aggregates, 10 value objects, repository protocols |
| Database | ✅ Complete | SQLAlchemy 2.0, Alembic, UnitOfWork, repositories |
| Authentication | ✅ Complete | Hybrid (IdP + TWIB JWT), RBAC, API keys |
| LLM Layer | ✅ Complete | OpenAI, Ollama, registry, streaming, usage tracking |
| Model Router | ✅ Complete | Cost/latency/capability routing, fallback chains |
| Agent Framework | ✅ Complete | 8 agents + Supervisor, memory, context, sandbox |
| Workflow Engine | ✅ Complete | DAG executor, checkpoints, templates, human-in-loop |
| REST API + Realtime | ✅ Complete | Workflow/Agent APIs, WebSocket, monitoring |
| Frontend | ✅ Complete | Next.js 15, 8 modules, full dashboard suite |
| **Production & Deployment** | 🟢 **In Progress** | Docker, K8s, Helm, CI/CD, environments |
| Analytics | 📋 Planned | Events, metrics, dashboards, reports, alerting |
| Production Hardening | 📋 Planned | Load/chaos testing, security, observability, ops |


## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Quick Start for Developers
1. Read this README completely
2. Review [docs/architecture.md](docs/architecture.md)
3. Review [docs/coding_guidelines.md](docs/coding_guidelines.md)
4. Set up development environment (see [DEVELOPMENT.md](docs/development_workflow.md))
5. Pick an issue from the backlog
6. Follow the PR process

### Code Review Checklist
- [ ] Follows coding standards
- [ ] Tests included and passing
- [ ] Documentation updated
- [ ] No circular dependencies
- [ ] Proper error handling
- [ ] Type hints complete
- [ ] Performance considered

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Security

See [SECURITY.md](SECURITY.md) for vulnerability reporting and security policies.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.