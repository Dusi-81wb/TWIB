# TWIB Documentation Index

> **Project:** TWIB (Total Workflow Intelligence Builder)
>
> **Document Type:** Master Navigation
>
> **Last Updated:** August 2026

The master navigation document for the TWIB documentation system. Use this index to locate any documentation resource.

---

## Core Documents

### Architecture & Design

- [architecture.md](architecture.md) — Authoritative system architecture: layers, principles, and the AI-native core.
- [folder_structure.md](folder_structure.md) — Complete directory tree and naming conventions reference.

### Governance

- [PROJECT_RULES.md](PROJECT_RULES.md) — Mandatory engineering rules every contributor and AI model must follow.
- [PROJECT_STATUS.md](PROJECT_STATUS.md) — Living status dashboard of current development state.

### Specifications

- [AI_SPECIFICATION.md](AI_SPECIFICATION.md) — AI system specification: agent contracts, lifecycle, and AI architecture.

### Technology & Process

- [TECH_STACK.md](TECH_STACK.md) — Chosen technologies and the rationale behind each selection.
- [roadmap.md](roadmap.md) — Long-term phased development plan and milestones.
- [development_workflow.md](development_workflow.md) — Environment setup, branching, PR, and release processes.
- [coding_guidelines.md](coding_guidelines.md) — Coding standards: naming, typing, patterns, and review checklist.
- [future_modules.md](future_modules.md) — Planned future modules and extensions beyond the core roadmap.

---

## Documentation Collections

- [adr/](adr/README.md) — Architecture Decision Records capturing the *why* behind each architectural choice.
- [diagrams/](diagrams/README.md) — Mermaid diagram sources describing the system visually.
- [api/](api/README.md) — Planned API contracts: endpoints, authentication, and status per resource group.
- [prompts/](prompts/README.md) — Agent prompt specifications: purpose, inputs, outputs, and constraints.
- [examples/](examples/README.md) — Illustrative examples for workflows, APIs, tools, prompts, and architecture.

---

## Recommended Reading Order

For new contributors and AI models:

1. [PROJECT_STATUS.md](PROJECT_STATUS.md) — Current state and what to work on next.
2. [architecture.md](architecture.md) — Understand the system.
3. [PROJECT_RULES.md](PROJECT_RULES.md) — Mandatory rules.
4. [AI_SPECIFICATION.md](AI_SPECIFICATION.md) — Understand the AI subsystem.
5. [folder_structure.md](folder_structure.md) — Where code lives.
6. [coding_guidelines.md](coding_guidelines.md) — How to write code.
7. [development_workflow.md](development_workflow.md) — How to contribute.

---

## Index of Subfolders

### ADR

| File | Title |
|------|-------|
| [adr/0001-clean-architecture.md](adr/0001-clean-architecture.md) | Clean Architecture |
| [adr/0002-fastapi.md](adr/0002-fastapi.md) | FastAPI |
| [adr/0003-postgresql.md](adr/0003-postgresql.md) | PostgreSQL |
| [adr/0004-model-router.md](adr/0004-model-router.md) | Model Router |
| [adr/0005-agent-orchestrator.md](adr/0005-agent-orchestrator.md) | Agent Orchestrator |
| [adr/0006-qdrant.md](adr/0006-qdrant.md) | Qdrant |
| [adr/0007-workflow-engine.md](adr/0007-workflow-engine.md) | Workflow Engine |

### Diagrams

| File | Description |
|------|-------------|
| [diagrams/system_architecture.mmd](diagrams/system_architecture.mmd) | High-level system architecture (TODO) |
| [diagrams/deployment_architecture.mmd](diagrams/deployment_architecture.mmd) | Deployment topology (TODO) |
| [diagrams/workflow_engine.mmd](diagrams/workflow_engine.mmd) | Workflow engine internals (TODO) |
| [diagrams/agent_orchestration.mmd](diagrams/agent_orchestration.mmd) | Agent coordination (TODO) |
| [diagrams/authentication_flow.mmd](diagrams/authentication_flow.mmd) | Authentication sequence (TODO) |
| [diagrams/database_schema.mmd](diagrams/database_schema.mmd) | Database schema (TODO) |
| [diagrams/rag_pipeline.mmd](diagrams/rag_pipeline.mmd) | RAG pipeline (TODO) |
| [diagrams/workflow_generation_sequence.mmd](diagrams/workflow_generation_sequence.mmd) | Workflow generation sequence (TODO) |

### API

| File | Resource Group |
|------|----------------|
| [api/authentication.md](api/authentication.md) | Authentication |
| [api/users.md](api/users.md) | Users |
| [api/organizations.md](api/organizations.md) | Organizations |
| [api/workflows.md](api/workflows.md) | Workflows |
| [api/agents.md](api/agents.md) | Agents |
| [api/billing.md](api/billing.md) | Billing |
| [api/websocket.md](api/websocket.md) | WebSocket |

### Prompts

| File | Agent |
|------|-------|
| [prompts/planner.md](prompts/planner.md) | Planner |
| [prompts/analyst.md](prompts/analyst.md) | Analyst |
| [prompts/architect.md](prompts/architect.md) | Architect |
| [prompts/researcher.md](prompts/researcher.md) | Researcher |
| [prompts/validator.md](prompts/validator.md) | Validator |
| [prompts/optimizer.md](prompts/optimizer.md) | Optimizer |
| [prompts/documentation.md](prompts/documentation.md) | Documentation |
| [prompts/supervisor.md](prompts/supervisor.md) | Supervisor |

### Examples

| File | Topic |
|------|-------|
| [examples/workflow_examples.md](examples/workflow_examples.md) | Workflow examples |
| [examples/api_examples.md](examples/api_examples.md) | API examples |
| [examples/tool_examples.md](examples/tool_examples.md) | Tool examples |
| [examples/prompt_examples.md](examples/prompt_examples.md) | Prompt examples |
| [examples/architecture_examples.md](examples/architecture_examples.md) | Architecture examples |

---

## Maintenance

- Keep this index updated whenever a document is added, removed, or renamed.
- Links are relative and resolve within the `docs/` directory.
