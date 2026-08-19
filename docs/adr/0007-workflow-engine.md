# ADR-0007 Workflow Engine

## Status

Accepted

## Context

TWIB generates and executes business workflows as directed graphs. The execution system must handle node scheduling, parallel execution, retries, checkpoints, timeouts, and resumption, while remaining independent of any specific orchestration vendor.

## Decision

Implement a dedicated Workflow Engine as a first-class internal module.

- Workflows are represented as directed graphs (nodes and edges)
- Engine handles node scheduling, dependency resolution, and parallel execution
- Supports retry policies, timeouts, checkpointing, and resume after failure
- Durable state management with defined execution/state machines
- Fully separate from agents (agents reason; engine executes)
- Abstraction keeps it independent of any external workflow-orchestration product

## Alternatives Considered

- Temporal: powerful but adds heavy external infrastructure and lock-in
- Airflow/Prefect: designed for batch pipelines, not AI-native graph generation
- Custom scheduler: riskier, but matches the AI-native execution model and stays replaceable
- Existing workflow SaaS: rejected, no runtime control or modularity

## Consequences

- Full control over execution semantics tailored to AI agents
- Significant implementation effort (scheduler, state, checkpoints, retries)
- Strong testability and the ability to swap to a vendor product later if needed
- Engine owns execution only; never business logic
