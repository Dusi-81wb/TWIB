# TWIB Project Rules

> **Version:** 1.0
>
> **Status:** Mandatory
>
> Every contributor, AI coding assistant, and developer must follow these rules.
>
> This document overrides personal coding preferences.

---

# 1. Purpose

This document defines the engineering rules governing the TWIB project.

It ensures that all future development remains consistent regardless of which AI model or human developer contributes.

Every generated module must comply with these rules.

---

# 2. Golden Rules

The following rules are absolute.

## Rule 1

Never modify the architecture without updating the Architecture Decision Records (ADR).

---

## Rule 2

Never violate Clean Architecture.

Dependencies always point inward.

---

## Rule 3

Never place business logic inside

- API Routers
- Controllers
- Database Models
- Middleware

Business logic belongs only inside Application Services.

---

## Rule 4

Every module must have one responsibility.

---

## Rule 5

Never access databases directly from services.

Always use repositories.

---

## Rule 6

Never access repositories from API routers.

---

## Rule 7

Never call LLM providers directly.

Always use the Model Router.

---

## Rule 8

Never call external APIs directly from agents.

Always use Tools.

---

## Rule 9

Every AI Agent must inherit from BaseAgent.

---

## Rule 10

Every external provider must implement its interface.

---

# 3. Project Structure

Never change the folder structure unless an ADR is created.

Current structure:

```text
backend/
frontend/
agents/
workflows/
llm/
database/
auth/
cache/
payments/
storage/
security/
analytics/
deployment/
tests/
docs/
```

---

# 4. Layer Rules

## Presentation

Responsible for

- UI

- Components

- Rendering

Never

- Business Logic

- Database Access

- AI Logic

---

## API

Responsible for

- Validation

- Authentication

- Serialization

Never

- Database Queries

- Workflow Logic

- AI Logic

---

## Application Services

Responsible for

- Business Logic

- Use Cases

- Orchestration

Never

- SQL

- HTTP

- HTML

---

## Agent Orchestrator

Responsible for

- Scheduling

- Coordination

- Retry

Never

- Prompt Engineering

- Persistence

---

## Workflow Engine

Responsible for

- Graph Execution

- Checkpoints

- Retry

Never

- Business Logic

---

## Context Manager

Responsible for

- Prompt Building

- Context Compression

- Token Budget

Never

- Model Selection

---

## Model Router

Responsible for

- Provider Selection

- Failover

- Streaming

Never

- Prompt Building

---

## Repository

Responsible for

Persistence only.

---

# 5. Naming Rules

Folders

snake_case

Files

snake_case

Classes

PascalCase

Functions

snake_case

Variables

snake_case

Constants

UPPER_CASE

Interfaces

Suffix with

Provider

Repository

Service

Manager

---

# 6. SOLID

Every implementation must satisfy

- SRP

- OCP

- LSP

- ISP

- DIP

---

# 7. Dependency Injection

Never instantiate dependencies manually.

Use dependency injection.

Avoid global state.

---

# 8. Repository Pattern

Every repository must expose an interface.

Implementations belong inside Infrastructure.

---

# 9. AI Rules

Agents never

- query databases

- send HTTP requests

- build SQL

Agents only

- reason

- plan

- validate

- optimize

Execution belongs elsewhere.

---

# 10. Model Rules

Never reference

OpenAI

DeepSeek

Nemotron

directly.

Always use

Model Router.

---

# 11. Tool Rules

Agents never call

GitHub

Slack

Database

Filesystem

directly.

Always use

Tool Registry.

---

# 12. Memory Rules

Context Manager owns

- Memory Retrieval

- Prompt Building

- Compression

Agents receive prepared context.

---

# 13. Security Rules

Never

Hardcode Secrets.

Never

Commit API Keys.

Never

Log Passwords.

Never

Return Internal Exceptions.

---

# 14. Logging Rules

Every request

Correlation ID.

Every exception

Structured logging.

JSON logs only.

---

# 15. Testing Rules

Every feature requires

Unit Tests.

Critical workflows require

Integration Tests.

---

# 16. Documentation Rules

Every major module must contain

README.md

Every public class requires docstrings.

Every architectural change requires ADR.

---

# 17. AI Handoff Rules

Before ending a development session:

Update

AI_HANDOFF.md

Include

- Current Phase
- Completed Work
- Pending Tasks
- Decisions Made
- Files Modified

---

# 18. Commit Rules

Commit after every completed sub-phase.

Example

```
Phase 1.1

FastAPI Foundation
```

Git Message

```
feat(phase-1.1): initialize FastAPI application
```

---

# 19. Current Development Order

```
Phase 0

↓

Phase 1

Foundation

↓

Phase 2

Authentication

↓

Phase 3

Database

↓

Phase 4

REST API

↓

Phase 5

LLM Layer

↓

Phase 6

Agents

↓

Phase 7

Workflow Engine

↓

Phase 8

Frontend

↓

Phase 9

Realtime

↓

Phase 10

Payments

↓

Phase 11

Deployment

↓

Production
```

---

# 20. Final Rule


# Documentation Lock

The following documents are considered architectural contracts.

- architecture.md
- PROJECT_RULES.md
- AI_SPECIFICATION.md
- TECH_STACK.md

These files must not be modified unless explicitly requested.

Architectural changes require:

- ADR
- Documentation update
- Project status update

Implementation phases must never silently modify them.

When uncertainty exists,

follow

architecture.md

instead of assumptions.

If architecture conflicts with generated code,

architecture wins.
