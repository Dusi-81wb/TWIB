# Documentation

## Purpose

All project documentation including architecture, coding standards, development workflow, and roadmap.

## Responsibilities

- Architecture documentation
- Folder structure reference
- Coding guidelines
- Development workflow
- Technology decisions
- Roadmap
- Future module specifications
- Architecture Decision Records (ADR)
- Diagrams
- API documentation
- Agent prompt specifications
- Examples

## What Belongs Here

- `architecture.md` - System architecture
- `folder_structure.md` - Directory reference
- `coding_guidelines.md` - Coding standards
- `development_workflow.md` - Dev process
- `roadmap.md` - Phase breakdown
- `future_modules.md` - Planned extensions
- `TECH_STACK.md` - Technology stack decisions
- `PROJECT_RULES.md` - Mandatory project rules
- `PROJECT_STATUS.md` - Current project status
- `AI_SPECIFICATION.md` - AI system specification
- `INDEX.md` - Master documentation navigation

## Documentation Tree

```
docs/
├── README.md                # Documentation overview
├── INDEX.md                 # Master navigation
├── architecture.md          # System architecture
├── folder_structure.md      # Directory reference
├── coding_guidelines.md     # Coding standards
├── development_workflow.md  # Dev process
├── roadmap.md               # Phase breakdown
├── future_modules.md        # Planned extensions
├── TECH_STACK.md            # Technology stack decisions
├── PROJECT_RULES.md         # Mandatory project rules
├── PROJECT_STATUS.md        # Current project status
├── AI_SPECIFICATION.md      # AI system specification
├── adr/                     # Architecture Decision Records
│   ├── README.md
│   ├── 0001-clean-architecture.md
│   ├── 0002-fastapi.md
│   ├── 0003-postgresql.md
│   ├── 0004-model-router.md
│   ├── 0005-agent-orchestrator.md
│   ├── 0006-qdrant.md
│   └── 0007-workflow-engine.md
├── diagrams/                # Mermaid diagram sources
│   ├── README.md
│   ├── system_architecture.mmd
│   ├── deployment_architecture.mmd
│   ├── workflow_engine.mmd
│   ├── agent_orchestration.mmd
│   ├── authentication_flow.mmd
│   ├── database_schema.mmd
│   ├── rag_pipeline.mmd
│   └── workflow_generation_sequence.mmd
├── api/                     # API documentation
│   ├── README.md
│   ├── authentication.md
│   ├── users.md
│   ├── organizations.md
│   ├── workflows.md
│   ├── agents.md
│   ├── billing.md
│   └── websocket.md
├── prompts/                 # Agent prompt specifications
│   ├── README.md
│   ├── planner.md
│   ├── analyst.md
│   ├── architect.md
│   ├── researcher.md
│   ├── validator.md
│   ├── optimizer.md
│   ├── documentation.md
│   └── supervisor.md
└── examples/                # Illustrative examples
    ├── README.md
    ├── workflow_examples.md
    ├── api_examples.md
    ├── tool_examples.md
    ├── prompt_examples.md
    └── architecture_examples.md
```

## What Must NEVER Belong Here

- Implementation code
- API documentation (auto-generated from code)
- Temporary notes

## Future Phases

- Phase 0: All docs created
- Ongoing: Updated with each phase