# TWIB Folder Structure Reference

> **Scope:** The tree below is the **target** repository structure. Top-level
> packages that are not yet implemented (`frontend/`, `agents/`, `workflows/`,
> `llm/`, `database/`, `auth/`, `cache/`, `vector_db/`, `storage/`, `payments/`,
> `analytics/`, `realtime/`, `security/`) currently exist only as README-only
> scaffolding. The `backend/` subtree reflects the **implemented** layout
> (see ADR-0008).

## Complete Directory Tree

```
TWIB/
├── .github/
│   └── workflows/           # CI/CD pipelines
├── frontend/                # Next.js Application
│   ├── public/              # Static assets
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   │   ├── (auth)/      # Auth route group
│   │   │   ├── (dashboard)/ # Dashboard route group
│   │   │   ├── api/         # API routes (proxy)
│   │   │   └── layout.tsx   # Root layout
│   │   ├── components/      # React components
│   │   │   ├── ui/          # Primitive components (Radix)
│   │   │   ├── forms/       # Form components
│   │   │   ├── workflow/    # Workflow builder components
│   │   │   ├── agent/       # Agent interaction components
│   │   │   └── charts/      # Analytics charts
│   │   ├── hooks/           # Custom React hooks
│   │   ├── lib/             # Utilities, clients
│   │   │   ├── api/         # TanStack Query hooks
│   │   │   ├── auth/        # Auth client
│   │   │   ├── websocket/   # Socket.io client
│   │   │   └── utils/       # Helpers
│   │   ├── stores/          # Zustand stores
│   │   ├── types/           # TypeScript types
│   │   └── styles/          # Global styles
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── .eslintrc.json
│   └── README.md
│
├── backend/                 # FastAPI Application (single package: app)
│   ├── app/                 # Application package (import root: app.*)
│   │   ├── __init__.py
│   │   ├── main.py          # Uvicorn entrypoint (app.main:app)
│   │   ├── application.py   # FastAPI application factory
│   │   ├── container.py     # DI container (dependency-injector)
│   │   ├── dependencies.py  # Shared FastAPI dependencies
│   │   ├── lifecycle.py     # Startup/shutdown logging
│   │   ├── api/             # Route Definitions (Thin)
│   │   │   ├── v1/          # API Version 1
│   │   │   │   ├── health.py
│   │   │   │   ├── auth.py          (Phase 2)
│   │   │   │   ├── users.py         (Phase 2)
│   │   │   │   ├── organizations.py (Phase 2)
│   │   │   │   ├── workflows.py     (Phase 4+)
│   │   │   │   ├── agents.py        (Phase 5+)
│   │   │   │   └── executions.py    (Phase 4+)
│   │   │   ├── router.py    # Root API router
│   │   │   ├── tags.py      # Centralized API tags
│   │   │   ├── openapi.py   # OpenAPI metadata
│   │   │   └── responses.py # Response helpers
│   │   ├── core/            # Configuration, logging, exceptions
│   │   │   ├── __init__.py
│   │   │   ├── settings.py  # Pydantic Settings
│   │   │   ├── config.py    # Settings loader (lru_cache)
│   │   │   ├── environments.py
│   │   │   ├── constants.py
│   │   │   ├── logging.py   # structlog setup
│   │   │   ├── exceptions.py# TWIBException hierarchy
│   │   │   ├── error_codes.py
│   │   │   └── handlers.py  # Global exception handlers
│   │   ├── middleware/      # Cross-Cutting Concerns
│   │   │   ├── __init__.py
│   │   │   ├── registration.py # Central registration
│   │   │   ├── request_id.py   # Correlation IDs
│   │   │   ├── security_headers.py
│   │   │   ├── cors.py         # CORS configuration
│   │   │   └── observability.py
│   │   ├── observability/   # Metrics/tracing protocols + request context
│   │   │   ├── __init__.py
│   │   │   ├── request_context.py
│   │   │   ├── events.py
│   │   │   ├── metrics.py   # Counter/Gauge/Histogram/Timer protocols
│   │   │   └── tracing.py   # Tracer/Span protocols
│   │   ├── schemas/         # Pydantic Models (Contracts)
│   │   │   ├── __init__.py
│   │   │   ├── common.py
│   │   │   ├── pagination.py
│   │   │   └── response.py  # SuccessResponse / ErrorResponse
│   │   ├── shared/          # Shared helpers
│   │   ├── services/        # Business Logic (future — Phase 3+)
│   │   ├── repositories/    # Repository interfaces (future)
│   │   ├── models/          # Domain models (future)
│   │   └── infrastructure/  # Adapters: auth, llm, db, cache (future)
│   │
│   ├── tests/               # Pytest Suite (imports app.*)
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   └── test_health.py
│   │
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── .python-version      # 3.12
│   ├── pytest.ini
│   ├── .env.example
│   └── README.md
│
├── agents/                  # AI Agent Implementations
│   ├── __init__.py
│   ├── base/                # Base agent infrastructure
│   │   ├── __init__.py
│   │   ├── agent.py         # BaseAgent class
│   │   ├── protocols.py     # Agent protocols
│   │   ├── context.py       # Execution context
│   │   ├── memory.py        # Agent memory
│   │   └── communication.py # Inter-agent messaging
│   │
│   ├── planner/             # Task Planning Agent
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── prompts.py
│   │   ├── strategies.py
│   │   └── schemas.py
│   │
│   ├── analyst/             # Requirements Analysis Agent
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── prompts.py
│   │   ├── extractors.py
│   │   └── schemas.py
│   │
│   ├── architect/           # Solution Architecture Agent
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── prompts.py
│   │   ├── patterns.py
│   │   └── schemas.py
│   │
│   ├── validator/           # Output Validation Agent
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── prompts.py
│   │   ├── rules.py
│   │   └── schemas.py
│   │
│   ├── optimizer/           # Workflow Optimization Agent
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── prompts.py
│   │   ├── analyzers.py
│   │   └── schemas.py
│   │
│   ├── researcher/          # Information Research Agent
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── prompts.py
│   │   ├── sources.py
│   │   └── schemas.py
│   │
│   ├── documentation/       # Auto-Documentation Agent
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── prompts.py
│   │   ├── templates.py
│   │   └── schemas.py
│   │
│   └── supervisor/          # Multi-Agent Orchestrator
│       ├── __init__.py
│       ├── agent.py
│       ├── prompts.py
│       ├── orchestrator.py
│       ├── state_machine.py
│       └── schemas.py
│
├── workflows/               # Workflow Engine
│   ├── __init__.py
│   ├── graph/               # Graph Data Structures
│   │   ├── __init__.py
│   │   ├── graph.py         # WorkflowGraph class
│   │   ├── node.py          # Node base class
│   │   ├── edge.py          # Edge base class
│   │   ├── algorithms.py    # Topological sort, cycles
│   │   ├── serialization.py # Import/export
│   │   └── visualization.py # Mermaid, GraphViz
│   │
│   ├── nodes/               # Node Type Definitions
│   │   ├── __init__.py
│   │   ├── base.py          # BaseNode class
│   │   ├── registry.py      # Node type registry
│   │   ├── llm_node.py      # LLM execution node
│   │   ├── tool_node.py     # Tool/function node
│   │   ├── condition_node.py # Conditional branching
│   │   ├── loop_node.py     # Iteration node
│   │   ├── parallel_node.py # Parallel execution
│   │   ├── human_node.py    # Human-in-the-loop
│   │   ├── agent_node.py    # Agent execution node
│   │   ├── subworkflow_node.py # Nested workflow
│   │   └── schemas.py       # Node schemas
│   │
│   ├── edges/               # Edge Type Definitions
│   │   ├── __init__.py
│   │   ├── base.py          # BaseEdge class
│   │   ├── sequence.py      # Sequential flow
│   │   ├── condition.py     # Conditional routing
│   │   ├── parallel.py      # Parallel split/join
│   │   ├── error.py         # Error handling edges
│   │   ├── compensation.py  # Saga compensation
│   │   └── schemas.py       # Edge schemas
│   │
│   ├── templates/           # Workflow Templates
│   │   ├── __init__.py
│   │   ├── registry.py      # Template registry
│   │   ├── base.py          # Template base class
│   │   ├── approval.py      # Approval workflow
│   │   ├── etl.py           # ETL pipeline
│   │   ├── notification.py  # Notification flow
│   │   ├── data_processing.py # Data processing
│   │   ├── schemas.py       # Template schemas
│   │   └── definitions/     # YAML/JSON templates
│   │
│   ├── executor/            # Execution Engine
│   │   ├── __init__.py
│   │   ├── executor.py      # WorkflowExecutor class
│   │   ├── scheduler.py     # Node scheduler
│   │   ├── state.py         # Execution state
│   │   ├── checkpoints.py   # Checkpoint manager
│   │   ├── retries.py       # Retry policies
│   │   ├── timeouts.py      # Timeout enforcement
│   │   ├── events.py        # Event emission
│   │   └── distributed.py   # Distributed execution
│   │
│   └── memory/              # Workflow Memory
│       ├── __init__.py
│       ├── store.py         # Memory store interface
│       ├── state.py         # State management
│       ├── checkpoints.py   # Checkpoint storage
│       ├── semantic.py      # Semantic memory (vectors)
│       ├── scopes.py        # Variable scoping
│       └── garbage.py       # GC policies
│
├── llm/                     # LLM Abstraction Layer
│   ├── __init__.py
│   ├── providers/           # Provider Implementations
│   │   ├── __init__.py
│   │   ├── base.py          # BaseProvider protocol
│   │   ├── openai.py        # OpenAI provider
│   │   ├── anthropic.py     # Anthropic provider
│   │   ├── ollama.py        # Ollama provider
│   │   ├── azure.py         # Azure OpenAI
│   │   ├── bedrock.py       # AWS Bedrock
│   │   ├── vertex.py        # Google Vertex AI
│   │   ├── factory.py       # Provider factory
│   │   └── capabilities.py  # Model capabilities
│   │
│   ├── router/              # Model Router
│   │   ├── __init__.py
│   │   ├── base.py          # Router protocol
│   │   ├── strategies/      # Routing strategies
│   │   │   ├── cost.py
│   │   │   ├── latency.py
│   │   │   ├── capability.py
│   │   │   ├── fallback.py
│   │   │   └── ab_test.py
│   │   ├── registry.py      # Model registry
│   │   ├── selector.py      # Model selector
│   │   └── analytics.py     # Routing analytics
│   │
│   ├── embeddings/          # Embedding Generation
│   │   ├── __init__.py
│   │   ├── service.py       # EmbeddingService
│   │   ├── providers/       # Embedding providers
│   │   │   ├── openai.py
│   │   │   ├── sentence_transformers.py
│   │   │   └── cohere.py
│   │   ├── cache.py         # Embedding cache
│   │   └── batch.py         # Batch processing
│   │
│   ├── tokenizer/           # Token Management
│   │   ├── __init__.py
│   │   ├── counter.py       # Token counter
│   │   ├── estimator.py     # Token estimator
│   │   ├── truncator.py     # Context truncation
│   │   └── cost.py          # Cost calculator
│   │
│   └── context/             # Context Window Management
│       ├── __init__.py
│       ├── builder.py       # ContextBuilder
│       ├── strategies/      # Window strategies
│       │   ├── sliding.py
│       │   ├── priority.py
│       │   └── compression.py
│       ├── budget.py        # Token budget
│       └── rag.py           # RAG context
│
├── auth/                    # Authentication & Authorization
│   ├── __init__.py
│   ├── providers/           # Auth provider adapters
│   │   ├── __init__.py
│   │   ├── auth0.py
│   │   ├── clerk.py
│   │   ├── oidc.py
│   │   └── api_key.py
│   ├── middleware.py        # Auth middleware
│   ├── rbac.py              # Role-based access control
│   ├── permissions.py       # Permission definitions
│   ├── jwt.py               # JWT utilities
│   ├── sessions.py          # Session management
│   └── schemas.py           # Auth schemas
│
├── database/                # Database Layer
│   ├── __init__.py
│   ├── models/              # SQLAlchemy Models
│   │   ├── __init__.py
│   │   ├── base.py          # Base model, mixins
│   │   ├── user.py
│   │   ├── organization.py
│   │   ├── workflow.py
│   │   ├── execution.py
│   │   ├── template.py
│   │   ├── agent.py
│   │   ├── billing.py
│   │   └── audit.py
│   │
│   ├── repositories/        # Repository Implementations
│   │   ├── __init__.py
│   │   ├── base.py          # BaseRepository
│   │   ├── unit_of_work.py  # UnitOfWork
│   │   ├── user.py
│   │   ├── organization.py
│   │   ├── workflow.py
│   │   ├── execution.py
│   │   ├── template.py
│   │   └── billing.py
│   │
│   ├── migrations/          # Alembic Migrations
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │
│   └── seed/                # Seed Data
│       ├── __init__.py
│       ├── development.py
│       ├── testing.py
│       ├── staging.py
│       └── production.py
│
├── vector_db/               # Vector Database
│   ├── __init__.py
│   ├── client.py            # Qdrant client wrapper
│   ├── collections/         # Collection schemas
│   │   ├── workflows.py
│   │   ├── documents.py
│   │   ├── embeddings.py
│   │   └── agent_memory.py
│   ├── search.py            # Search service
│   ├── indexer.py           # Index management
│   └── schemas.py
│
├── cache/                   # Caching Layer
│   ├── __init__.py
│   ├── client.py            # Redis client wrapper
│   ├── service.py           # CacheService
│   ├── decorators.py        # @cached decorator
│   ├── locks.py             # Distributed locks
│   ├── streams.py           # Redis Streams
│   └── pubsub.py            # Pub/Sub
│
├── payments/                # Payment Processing
│   ├── __init__.py
│   ├── stripe/              # Stripe integration
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── webhooks.py
│   │   ├── subscriptions.py
│   │   ├── usage.py
│   │   └── invoices.py
│   ├── service.py           # BillingService
│   ├── pricing.py           # Price calculator
│   ├── metering.py          # Usage metering
│   └── schemas.py
│
├── realtime/                # Real-time Infrastructure
│   ├── __init__.py
│   ├── server.py            # WebSocket server
│   ├── presence.py          # Presence system
│   ├── rooms.py             # Room management
│   ├── events.py            # Event broadcasting
│   ├── collaboration.py     # Collaborative editing
│   └── schemas.py
│
├── analytics/               # Analytics & Monitoring
│   ├── __init__.py
│   ├── events/              # Event tracking
│   │   ├── collector.py
│   │   ├── processor.py
│   │   └── schemas.py
│   ├── metrics/             # Metric aggregation
│   │   ├── aggregator.py
│   │   ├── querier.py
│   │   └── schemas.py
│   ├── dashboards/          # Dashboard data APIs
│   │   ├── workflow.py
│   │   ├── agent.py
│   │   ├── billing.py
│   │   └── system.py
│   ├── reports/             # Report generation
│   │   ├── builder.py
│   │   ├── templates.py
│   │   └── export.py
│   └── alerts/              # Alerting
│       ├── evaluator.py
│       ├── notifier.py
│       └── rules.py
│
├── security/                # Security Utilities
│   ├── __init__.py
│   ├── crypto.py            # Encryption utilities
│   ├── secrets.py           # Secrets management
│   ├── sanitization.py      # Input sanitization
│   ├── pii.py               # PII detection
│   ├── audit.py             # Audit logging
│   └── compliance.py        # Compliance helpers
│
├── storage/                 # File Storage
│   ├── __init__.py
│   ├── providers/           # Storage providers
│   │   ├── __init__.py
│   │   ├── s3.py
│   │   ├── gcs.py
│   │   ├── azure.py
│   │   └── local.py
│   ├── service.py           # StorageService
│   ├── upload.py            # Upload handling
│   ├── lifecycle.py         # Lifecycle policies
│   └── schemas.py
│
├── docker/                  # Docker Configurations
│   ├── development/
│   │   └── docker-compose.yml  # Dev stack (backend, postgres, redis, qdrant)
│   ├── production/
│   │   └── docker-compose.yml  # Production stack
│   └── README.md
│
├── deployment/              # Deployment Manifests
│   ├── k8s/
│   │   ├── base/
│   │   │   ├── namespace.yaml
│   │   │   ├── configmap.yaml
│   │   │   ├── secrets.yaml
│   │   │   ├── backend-deployment.yaml
│   │   │   ├── frontend-deployment.yaml
│   │   │   ├── ingress.yaml
│   │   │   └── services.yaml
│   │   ├── overlays/
│   │   │   ├── development/
│   │   │   ├── staging/
│   │   │   └── production/
│   │   └── monitoring/
│   │       ├── prometheus.yaml
│   │       ├── grafana.yaml
│   │       └── alertmanager.yaml
│   ├── helm/
│   │   ├── twib/
│   │   │   ├── Chart.yaml
│   │   │   ├── values.yaml
│   │   │   ├── values-dev.yaml
│   │   │   ├── values-staging.yaml
│   │   │   ├── values-prod.yaml
│   │   │   └── templates/
│   │   └── dependencies/
│   ├── scripts/
│   │   ├── deploy.sh
│   │   ├── rollback.sh
│   │   └── promote.sh
│   └── environments/
│       ├── development.yaml
│       ├── staging.yaml
│       └── production.yaml
│
├── tests/                   # (README-only scaffolding — active tests live in backend/tests/)
│
├── docs/                    # Documentation
│   ├── architecture.md
│   ├── folder_structure.md
│   ├── coding_guidelines.md
│   ├── development_workflow.md
│   ├── roadmap.md
│   ├── future_modules.md
│   └── TECH_STACK.md
│
├── scripts/                 # Operational Scripts
│   ├── dev-setup.sh
│   ├── db-migrate.sh
│   ├── db-seed.sh
│   ├── lint.sh
│   ├── test.sh
│   └── typecheck.sh
│
├── Dockerfile              # Multi-stage backend image (development + runtime)
├── .dockerignore
├── .gitignore
├── .editorconfig
├── .pre-commit-config.yaml
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── CHANGELOG.md
└── README.md
# Planned (future phases): root pyproject.toml, package.json, Makefile,
# scripts/, and .github/workflows/
```

## Directory Naming Conventions

| Type | Convention | Examples |
|------|------------|----------|
| Packages | `snake_case` | `backend`, `agents`, `workflows` |
| Modules | `snake_case.py` | `user_service.py`, `workflow_executor.py` |
| Test files | `test_*.py` | `test_user_service.py` |
| Config files | `snake_case.yaml/.toml/.ini` | `docker-compose.yml`, `pyproject.toml` |
| Scripts | `kebab-case.sh` | `dev-setup.sh`, `db-migrate.sh` |

## File Organization Rules

1. **One class per file** (generally)
2. **`__init__.py` exports public API** only
3. **Protocols in `protocols.py`** or `protocols/` directory
4. **Schemas in `schemas.py`** or `schemas/` directory
5. **Exceptions in `exceptions.py`** or `exceptions/` directory
6. **Tests mirror source structure** under `tests/`
7. **No circular imports** - use protocols to break cycles