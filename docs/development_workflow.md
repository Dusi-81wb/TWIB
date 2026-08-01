# TWIB Development Workflow

## Overview

This document defines the complete development workflow for TWIB, from environment setup to production deployment.

## Environment Setup

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12 | Backend runtime |
| Node.js | 20+ | Frontend runtime |
| Docker | 24+ | Containerization |
| Docker Compose | 2+ | Local orchestration |
| PostgreSQL | 15+ | Primary database |
| Redis/Valkey | 7+ | Cache & streams |
| Qdrant | 1.8+ | Vector database |
| Git | 2.40+ | Version control |

### Backend Setup

```bash
# Navigate to backend
cd TWIB/backend

# Install dependencies with uv (uv.lock is committed)
uv sync --all-groups

# Copy environment template
cp .env.example .env

# Configure .env with local settings
# DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/twib
# REDIS_URL=redis://localhost:6379/0
# QDRANT_URL=http://localhost:6333

# Run the API in development (hot reload)
uv run uvicorn app.main:app --reload
```

### Frontend Setup

```bash
# Navigate to frontend
cd TWIB/frontend

# Install dependencies (when ready)
npm install

# Copy environment template
cp .env.example .env.local

# Configure .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000
# NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Docker Development Environment

```bash
# From root directory
cd TWIB

# Start all services (backend + postgres + redis + qdrant)
docker compose -f docker/development/docker-compose.yml up -d

# View logs
docker compose -f docker/development/docker-compose.yml logs -f

# Stop services
docker compose -f docker/development/docker-compose.yml down
```

The production stack lives at `docker/production/docker-compose.yml`
(see `backend/README.md` → Docker Production for build and run instructions).

---

## Branching Strategy

### Branch Structure
```
main (protected, production-ready)
  └── develop (integration branch)
        ├── feature/* (new features)
        ├── fix/* (bug fixes)
        ├── docs/* (documentation updates)
        ├── refactor/* (code improvements)
        ├── perf/* (performance improvements)
        └── test/* (test additions)
```

### Branch Naming
```
feature/workflow-parallel-execution
fix/agent-token-counting
docs/api-v1-workflows
refactor/repository-pattern
perf/llm-response-caching
test/integration-vector-db
```

### Branch Lifecycle
1. Create from `develop`
2. Implement changes with tests
3. Run local quality checks
4. Push and create PR
5. Code review + CI
6. Squash merge to `develop`
7. Delete branch

---

## Commit Convention

### Format (Conventional Commits)
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no logic change |
| `refactor` | Code restructuring |
| `perf` | Performance improvement |
| `test` | Adding/updating tests |
| `chore` | Maintenance, tooling |
| `ci` | CI/CD changes |

### Examples
```
feat(workflow): add parallel node execution

Implement ParallelNode type with concurrent branch
execution support. Includes timeout handling and
error aggregation across branches.

Closes #123
```

```
fix(llm): handle token limit exceeded gracefully

Add automatic context truncation when token limit
is exceeded. Falls back to smaller models if needed.

Fixes #456
```

```
docs(api): update workflow generation endpoints

Add request/response examples for POST /workflows/generate
and GET /workflows/{id}/status endpoints.
```

---

## Pull Request Process

### PR Requirements
1. **Linked Issue**: Every PR references an issue (`Closes #123` or `Refs #123`)
2. **Description**: Clear what/why, not just what
3. **Tests**: Unit + integration tests for new logic
4. **Documentation**: Updated if API/schema changes
5. **Quality Gates**: All CI checks pass

### PR Template
```markdown
## Description
Brief summary of changes.

## Type
- [ ] Feature
- [ ] Bug Fix
- [ ] Documentation
- [ ] Refactor
- [ ] Performance
- [ ] Test

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Follows coding guidelines
- [ ] Type hints complete
- [ ] Docstrings updated
- [ ] No circular imports
- [ ] Lint passes
- [ ] Typecheck passes
- [ ] All tests pass
```

### Review Process
1. **Automated checks** run (lint, typecheck, tests, build)
2. **Code review** by at least 1 maintainer
3. **Address feedback** (push new commits)
4. **Squash merge** to `develop`
5. **Branch deleted** automatically

---

## Quality Gates

### Local Development
```bash
# Backend
cd backend
ruff check .              # Lint
ruff format .             # Format
mypy .                    # Typecheck
pytest                    # Tests

# Frontend
cd frontend
npm run lint              # ESLint
npm run typecheck         # TypeScript
npm test                  # Tests
```

### CI Pipeline (GitHub Actions)
```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [develop, main]
  push:
    branches: [develop, main]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: cd backend && uv sync --frozen
      - run: cd backend && ruff check .
      - run: cd backend && ruff format --check .
      - run: cd backend && mypy .
      - run: cd backend && pytest --cov-fail-under=80

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: cd frontend && npm ci
      - run: cd frontend && npm run lint
      - run: cd frontend && npm run typecheck
      - run: cd frontend && npm test -- --coverage

  docker:
    runs-on: ubuntu-latest
    needs: [backend]
    steps:
      - uses: actions/checkout@v4
      - run: docker build -f Dockerfile -t twib-backend .
      # Frontend build job is added when the frontend exists (Phase 6+)
```

### Quality Standards
| Check | Threshold |
|-------|-----------|
| Test Coverage | ≥ 80% (backend), ≥ 70% (frontend) |
| Lint Errors | 0 |
| Type Errors | 0 |
| Critical Vulnerabilities | 0 |
| Build Success | Required |

---

## Release Process

### Versioning
**Semantic Versioning** (MAJOR.MINOR.PATCH)
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

### Release Branches
```
release/v1.2.0 (from develop)
  ├── Version bump
  ├── Changelog update
  ├── Final testing
  └── Tag v1.2.0
```

### Release Steps
1. Create `release/vX.Y.Z` from `develop`
2. Update version in `pyproject.toml`, `package.json`
3. Update `CHANGELOG.md`
4. Run full test suite
5. Deploy to staging
6. Run integration tests on staging
7. Merge to `main` with tag
8. Deploy to production
9. Merge `main` back to `develop`

### Hotfix Process
```
hotfix/v1.2.1 (from main)
  ├── Fix applied
  ├── Version bump (PATCH)
  ├── Changelog update
  ├── Deploy to production
  └── Merge to main + develop
```

---

## Development Commands

### Makefile (Root)
```makefile
# TWIB Development Commands

.PHONY: help dev-up dev-down dev-logs

help:
	@echo "TWIB Development Commands"
	@echo "  make dev-up       Start development environment"
	@echo "  make dev-down     Stop development environment"
	@echo "  make dev-logs     View development logs"
	@echo "  make lint         Run all linters"
	@echo "  make typecheck    Run all type checkers"
	@echo "  make test         Run all tests"
	@echo "  make format       Format all code"
	@echo "  make clean        Clean build artifacts"

dev-up:
	docker compose -f docker/development/docker-compose.yml up -d

dev-down:
	docker compose -f docker/development/docker-compose.yml down

dev-logs:
	docker compose -f docker/development/docker-compose.yml logs -f

lint:
	cd backend && ruff check .
	cd frontend && npm run lint

typecheck:
	cd backend && mypy .
	cd frontend && npm run typecheck

test:
	cd backend && pytest
	cd frontend && npm test

format:
	cd backend && ruff format .
	cd frontend && npm run format

clean:
	docker compose -f docker/development/docker-compose.yml down -v
	rm -rf backend/.venv frontend/node_modules
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
```

---

## Debugging

### Backend Debugging
```bash
# Attach debugger to running container
docker exec -it twib-backend python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Or run locally with debugger
cd backend
python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m uvicorn app.main:app --reload
```

### Database Debugging
```bash
# Connect to PostgreSQL
docker exec -it twib-postgres psql -U twib -d twib

# Run migration manually
cd backend
alembic upgrade head
alembic downgrade -1
```

### Frontend Debugging
```bash
# Start with debugging
cd frontend
npm run dev

# Build for production testing
npm run build
npm run start
```

---

## Monitoring Development

### Local Observability
```bash
# Start monitoring stack (planned — monitoring compose is not yet created)
# docker compose -f docker/development/docker-compose.monitoring.yml up -d

# Access
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)
# Jaeger: http://localhost:16686
```

### Log Analysis
```bash
# Structured logs in JSON
docker logs twib-backend | jq '. | select(.level=="error")'

# Filter by correlation ID
docker logs twib-backend | jq 'select(.correlation_id=="abc-123")'
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Ensure `uv sync --all-groups` in backend |
| `ImportError` circular | Check for missing protocols, use `TYPE_CHECKING` |
| Database connection failed | Verify `DATABASE_URL` in `.env`, check container health |
| Redis connection failed | Verify `REDIS_URL`, check container health |
| Frontend API errors | Check `NEXT_PUBLIC_API_URL`, verify backend running |
| TypeCheck errors | Run `mypy .` with `--show-error-codes` for details |

### Performance Profiling
```bash
# Backend profiling
cd backend
python -m cProfile -o profile.stats -m uvicorn app.main:app
# Analyze with snakeviz
snakeviz profile.stats

# Frontend profiling
cd frontend
npm run build --profile
# Open Chrome DevTools Performance tab
```

---

## Security Practices

### Secrets Management
- **Never commit secrets** to git
- Use `.env` files (gitignored) for local development
- Use Vault/Secrets Manager for CI/CD and production
- Rotate secrets regularly

### Dependency Scanning
```bash
# Backend
cd backend
pip-audit
safety check

# Frontend
cd frontend
npm audit
npm audit fix
```

---

## Onboarding Checklist

For new developers:
- [ ] Read `README.md` completely
- [ ] Read `docs/architecture.md`
- [ ] Read `docs/coding_guidelines.md`
- [ ] Read `docs/development_workflow.md`
- [ ] Set up development environment
- [ ] Run `make dev-up` and verify all services healthy
- [ ] Run `make test` and verify all tests pass
- [ ] Pick a `good first issue` from backlog
- [ ] Submit first PR following the process