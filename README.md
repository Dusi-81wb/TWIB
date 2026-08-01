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

### Phase 0: Architecture (Current)
- [x] Folder structure
- [x] Documentation
- [x] Coding standards
- [x] Tech stack decisions

### Phase 1: Foundation
- [ ] Project bootstrap (pyproject.toml, package.json)
- [ ] Configuration system
- [ ] Logging infrastructure
- [ ] Exception hierarchy
- [ ] DI container setup

### Phase 2: Authentication
- [ ] Auth provider integration
- [ ] JWT validation middleware
- [ ] Role-based access control
- [ ] API key management

### Phase 3: Database
- [ ] SQLAlchemy models
- [ ] Repository base & implementations
- [ ] Migration framework
- [ ] Seed data

### Phase 4: REST APIs
- [ ] API router structure
- [ ] Request/response schemas
- [ ] CRUD endpoints
- [ ] Pagination, filtering, sorting

### Phase 5: LLM Integration
- [ ] Provider abstraction
- [ ] OpenAI, Anthropic, Ollama adapters
- [ ] Token tracking
- [ ] Rate limiting

### Phase 6: Model Router
- [ ] Routing strategies
- [ ] Cost optimization
- [ ] Fallback chains
- [ ] A/B testing framework

### Phase 7: Agent Framework
- [ ] Base agent class
- [ ] Agent communication protocol
- [ ] Planner, Analyst, Architect agents
- [ ] Validator, Optimizer agents
- [ ] Researcher, Documentation agents
- [ ] Supervisor orchestrator

### Phase 8: Workflow Engine
- [ ] Graph data structures
- [ ] Node/edge definitions
- [ ] Execution engine
- [ ] State management
- [ ] Template system

### Phase 9: Frontend Dashboard
- [ ] Next.js setup
- [ ] Authentication UI
- [ ] Workflow builder
- [ ] Execution monitoring
- [ ] Agent interaction UI

### Phase 10: Real-time Collaboration
- [ ] WebSocket server
- [ ] Presence system
- [ ] Collaborative editing
- [ ] Live execution updates

### Phase 11: Payments
- [ ] Stripe integration
- [ ] Subscription management
- [ ] Usage-based billing
- [ ] Invoice generation

### Phase 12: Analytics
- [ ] Event tracking
- [ ] Dashboard metrics
- [ ] Custom reports
- [ ] Export capabilities

### Phase 13: Deployment
- [ ] Docker images
- [ ] Kubernetes manifests
- [ ] Helm charts
- [ ] Environment promotion

### Phase 14: Production Hardening
- [ ] Load testing
- [ ] Chaos engineering
- [ ] Security audit
- [ ] Disaster recovery
- [ ] Runbooks

---

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