# Contributing to TWIB

Thank you for your interest in contributing to TWIB (Total Workflow Intelligence Builder). This document outlines the contribution process, standards, and expectations.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Environment](#development-environment)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Review Checklist](#review-checklist)
- [Issue Templates](#issue-templates)

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing. We are committed to fostering a welcoming, respectful, and inclusive community.

## How to Contribute

### Ways to Contribute

1. **Report Bugs**: Open an issue with detailed reproduction steps
2. **Feature Requests**: Propose new features with use cases
3. **Documentation**: Improve docs, fix typos, add examples
4. **Code**: Implement features or fix bugs following the roadmap
5. **Review**: Participate in code reviews
6. **Testing**: Help test releases and report issues

### Getting Started

1. **Fork** the repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/your-username/TWIB.git
   cd TWIB
   ```
3. **Create a branch** from `develop`:
   ```bash
   git checkout -b feature/your-feature-name develop
   ```
4. **Set up** the development environment (below)
5. **Implement** your changes with tests
6. **Run** all quality checks
7. **Push** your branch and open a PR

## Development Environment

See [docs/development_workflow.md](docs/development_workflow.md) for full setup instructions.

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker + Docker Compose
- PostgreSQL 15+
- Redis 7+ (Valkey)

### Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
pip install -e ".[dev]"
cp .env.example .env
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
```

### Start Development Services

```bash
cd TWIB
docker-compose -f docker/docker-compose.dev.yml up -d
```

## Coding Standards

**Mandatory reading**: [docs/coding_guidelines.md](docs/coding_guidelines.md)

### Key Rules

- **Clean Architecture**: No business logic in routers; logic in services
- **Repository Pattern**: Repositories only touch the database
- **Dependency Injection**: Constructor injection only
- **Type Hints**: Mandatory on all public APIs
- **Docstrings**: Google style on all public classes/methods
- **Async**: All I/O must be async; never block the event loop
- **Naming**: snake_case files/functions, PascalCase classes
- **No Circular Imports**: Use protocols to break cycles

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

Closes #<issue>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`

## Testing

- **Unit Tests**: `tests/unit/` - must be fast and isolated
- **Integration Tests**: `tests/integration/` - use real DB/external services
- **E2E Tests**: `tests/e2e/` - full user flows

### Running Tests

```bash
# Backend
cd backend
pytest --cov=backend --cov-fail-under=80

# Frontend
cd frontend
npm test -- --coverage
```

### Test Coverage Requirements

- Backend: ≥ 80%
- Frontend: ≥ 70%

## Pull Request Process

1. **Target `develop`**: All PRs merge into `develop`
2. **Reference Issue**: Every PR links an issue (`Closes #123`)
3. **Small, Focused**: Keep PRs under 500 lines; split large changes
4. **CI Must Pass**: All checks (lint, typecheck, tests, build)
5. **Review Required**: At least 1 maintainer approval
6. **Squash Merge**: Commits squashed into one clean commit

### PR Description Template

```markdown
## Description
[Brief summary of changes]

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

## Review Checklist

Reviewers verify:

- [ ] Architecture compliance (Clean Architecture layers)
- [ ] Naming conventions followed
- [ ] Type hints present and correct
- [ ] Error handling proper (no bare except)
- [ ] Async/await used correctly
- [ ] No circular imports
- [ ] Tests cover new logic
- [ ] Documentation updated if needed
- [ ] No secrets or sensitive data
- [ ] Performance considered

## Issue Templates

### Bug Report

```
**Describe the bug**
[Clear description]

**To Reproduce**
1. Step 1
2. Step 2

**Expected behavior**
[What should happen]

**Actual behavior**
[What happens instead]

**Environment**
- OS:
- Python version:
- Node version:
- Docker version:

**Logs/Screenshots**
[Relevant logs or screenshots]
```

### Feature Request

```
**Problem/Use Case**
[What problem does this solve?]

**Proposed Solution**
[How should it work?]

**Alternative Approaches**
[Other options considered]

**Acceptance Criteria**
- [ ] Criteria 1
- [ ] Criteria 2
```

## Branch Protection

The `main` branch is protected:
- No direct pushes
- Requires CI to pass
- Requires review
- Linear history (squash only)

## Getting Help

- **Docs**: Read the docs/ directory
- **Issues**: Search existing issues first
- **Discussions**: Start a discussion for questions

## Thank You

Every contribution, big or small, helps build TWIB. We appreciate your time and effort!