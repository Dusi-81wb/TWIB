# TWIB Folder Structure Reference

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
├── backend/                 # FastAPI Application
│   ├── api/                 # Route Definitions (Thin)
│   │   ├── v1/              # API Version 1
│   │   │   ├── routes/      # Route modules
│   │   │   │   ├── auth.py
│   │   │   │   ├── users.py
│   │   │   │   ├── organizations.py
│   │   │   │   ├── workflows.py
│   │   │   │   ├── agents.py
│   │   │   │   ├── executions.py
│   │   │   │   ├── templates.py
│   │   │   │   ├── analytics.py
│   │   │   │   └── billing.py
│   │   │   ├── dependencies.py  # API-specific DI
│   │   │   └── router.py    # Main v1 router
│   │   ├── dependencies.py  # Shared API dependencies
│   │   └── router.py        # Root API router
│   │
│   ├── middleware/          # Cross-Cutting Concerns
│   │   ├── __init__.py
│   │   ├── logging.py       # Request/response logging
│   │   ├── auth.py          # JWT validation
│   │   ├── rate_limit.py    # Rate limiting
│   │   ├── cors.py          # CORS configuration
│   │   ├── errors.py        # Exception handlers
│   │   ├── metrics.py       # Prometheus metrics
│   │   └── request_id.py    # Correlation IDs
│   │
│   ├── dependencies/        # Dependency Injection
│   │   ├── __init__.py
│   │   ├── container.py     # Main DI container
│   │   ├── providers.py     # Provider registrations
│   │   ├── protocols/       # Interface definitions
│   │   │   ├── repository.py
│   │   │   ├── service.py
│   │   │   ├── llm.py
│   │   │   ├── cache.py
│   │   │   └── storage.py
│   │   └── scopes.py        # Scope definitions
│   │
│   ├── config/              # Configuration Management
│   │   ├── __init__.py
│   │   ├── settings.py      # Pydantic Settings
│   │   ├── database.py      # Database config
│   │   ├── redis.py         # Redis config
│   │   ├── llm.py           # LLM provider config
│   │   ├── auth.py          # Auth config
│   │   ├── storage.py       # Storage config
│   │   └── feature_flags.py # Feature flags
│   │
│   ├── websocket/           # Real-time Communication
│   │   ├── __init__.py
│   │   ├── router.py        # WebSocket routes
│   │   ├── manager.py       # Connection manager
│   │   ├── handlers/        # Message handlers
│   │   │   ├── presence.py
│   │   │   ├── workflow.py
│   │   │   └── collaboration.py
│   │   ├── schemas.py       # Message schemas
│   │   └── auth.py          # WS authentication
│   │
│   ├── services/            # Business Logic (CORE)
│   │   ├── __init__.py
│   │   ├── base.py          # Base service class
│   │   ├── user/            # User management
│   │   │   ├── service.py
│   │   │   ├── protocols.py
│   │   │   └── events.py
│   │   ├── organization/    # Organization management
│   │   ├── workflow/        # Workflow orchestration
│   │   │   ├── generation.py
│   │   │   ├── execution.py
│   │   │   ├── template.py
│   │   │   └── validation.py
│   │   ├── agent/           # Agent coordination
│   │   │   ├── planner.py
│   │   │   ├── analyst.py
│   │   │   ├── architect.py
│   │   │   ├── validator.py
│   │   │   ├── optimizer.py
│   │   │   ├── researcher.py
│   │   │   ├── documentation.py
│   │   │   └── supervisor.py
│   │   ├── billing/         # Billing & subscriptions
│   │   ├── analytics/       # Analytics aggregation
│   │   └── notification/    # Notifications
│   │
│   ├── schemas/             # Pydantic Models (Contracts)
│   │   ├── __init__.py
│   │   ├── base.py          # Base schemas
│   │   ├── common.py        # Shared types
│   │   ├── errors.py        # Error responses
│   │   ├── pagination.py    # Pagination schemas
│   │   ├── auth/            # Auth schemas
│   │   ├── user/            # User schemas
│   │   ├── organization/    # Org schemas
│   │   ├── workflow/        # Workflow schemas
│   │   ├── agent/           # Agent schemas
│   │   ├── execution/       # Execution schemas
│   │   ├── template/        # Template schemas
│   │   ├── analytics/       # Analytics schemas
│   │   └── billing/         # Billing schemas
│   │
│   ├── exceptions/          # Exception Hierarchy
│   │   ├── __init__.py
│   │   ├── base.py          # Base exceptions
│   │   ├── http.py          # HTTP exceptions
│   │   ├── domain/          # Domain exceptions
│   │   │   ├── user.py
│   │   │   ├── workflow.py
│   │   │   ├── agent.py
│   │   │   └── billing.py
│   │   ├── infrastructure/  # Infrastructure exceptions
│   │   │   ├── database.py
│   │   │   ├── llm.py
│   │   │   ├── cache.py
│   │   │   └── storage.py
│   │   └── handlers.py      # Exception handlers
│   │
│   ├── utils/               # Pure Utilities
│   │   ├── __init__.py
│   │   ├── strings.py       # String helpers
│   │   ├── dates.py         # Date/time helpers
│   │   ├── crypto.py        # Crypto helpers
│   │   ├── validation.py    # Validation helpers
│   │   ├── collections.py   # Collection helpers
│   │   ├── async.py         # Async helpers
│   │   ├── serialization.py # Serialization
│   │   └── logging.py       # Logging setup
│   │
│   ├── core/                # Application Bootstrap
│   │   ├── __init__.py
│   │   ├── app.py           # FastAPI factory
│   │   ├── lifespan.py      # Lifespan events
│   │   ├── health.py        # Health checks
│   │   └── openapi.py       # OpenAPI customization
│   │
│   ├── pyproject.toml
│   ├── poetry.lock
│   ├── .python-version
│   ├── pytest.ini
│   ├── .ruff.toml
│   ├── .mypy.ini
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
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   ├── docker-compose.yml
│   ├── docker-compose.dev.yml
│   ├── docker-compose.prod.yml
│   ├── .dockerignore
│   └── scripts/
│       ├── build.sh
│       └── push.sh
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
├── tests/                   # Test Suite
│   ├── __init__.py
│   ├── conftest.py          # Pytest configuration
│   ├── unit/                # Unit Tests
│   │   ├── test_services/
│   │   ├── test_agents/
│   │   ├── test_workflows/
│   │   ├── test_llm/
│   │   └── test_utils/
│   ├── integration/         # Integration Tests
│   │   ├── test_database/
│   │   ├── test_llm_providers/
│   │   ├── test_vector_db/
│   │   ├── test_cache/
│   │   └── test_payments/
│   ├── e2e/                 # End-to-End Tests
│   │   ├── test_workflow_generation.py
│   │   ├── test_workflow_execution.py
│   │   ├── test_agent_collaboration.py
│   │   └── test_auth_flow.py
│   ├── contract/            # Contract Tests
│   │   ├── test_api_v1.py
│   │   └── test_schemas.py
│   ├── performance/         # Performance Tests
│   │   ├── test_api_load.py
│   │   ├── test_workflow_throughput.py
│   │   └── test_llm_latency.py
│   ├── chaos/               # Chaos Engineering
│   │   ├── test_db_failure.py
│   │   ├── test_llm_failure.py
│   │   └── test_network_partition.py
│   └── fixtures/            # Test Fixtures
│       ├── factories.py
│       ├── data.py
│       └── mocks.py
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
├── .gitignore
├── .editorconfig
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── CHANGELOG.md
├── README.md
├── pyproject.toml           # Root Python config (for shared tools)
├── package.json             # Root Node config (for shared tools)
└── Makefile                 # Common commands
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