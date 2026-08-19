# ADR-0005 Agent Orchestrator

## Status

Accepted

## Context

TWIB uses multiple AI agents (planner, analyst, architect, validator, optimizer, researcher, documentation) coordinated by a supervisor. Agents must collaborate without coupling to each other or to infrastructure, and new agents must be added without modifying existing code.

## Decision

Introduce an Agent Orchestrator (Supervisor) as the central coordination layer.

- Orchestrator decides which agents execute, execution order, parallelism, and dependencies
- Agents never communicate directly; all messages pass through the orchestrator
- Orchestrator never performs reasoning, prompt building, persistence, or external calls
- Every agent inherits from `BaseAgent` with a standard `execute(context) -> AgentResult` contract
- Agents remain stateless; all state lives in the Context Manager and Workflow Engine
- Future agents register automatically without core modifications

## Alternatives Considered

- Direct agent-to-agent messaging: rejected, creates circular dependencies
- Monolithic AI pipeline: rejected, hard to extend and test
- No coordinator: rejected, no conflict resolution or orchestration

## Consequences

- Loose coupling and independent testability of agents
- Central point for scheduling, retry, and human-approval routing
- Requires a well-defined agent communication protocol
- Orchestrator is a single point of coordination (must be resilient)
