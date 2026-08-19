# ADR-0001 Clean Architecture

## Status

Accepted

## Context

TWIB is an enterprise AI-native platform with many modules (agents, workflows, LLM, payments, realtime). Without a strict structure, dependencies can drift, modules become coupled, and replacement becomes costly. The project needs a long-term architectural rule that every contributor follows.

## Decision

Adopt Clean Architecture with strict layer separation and the Dependency Rule (dependencies always point inward):

- Presentation → API → Application Services → Domain → Repository Interfaces → Infrastructure
- Business logic lives only in Application Services
- Repositories only communicate with databases
- Every external system implements an interface defined by an inner layer

## Alternatives Considered

- Monolithic architecture: rejected, no module replaceability
- MVC pattern: rejected, business logic leaks into controllers
- Hexagonal (Ports & Adapters): similar benefits, but Clean Architecture already mandated by PROJECT_RULES

## Consequences

- Strict discipline required from all contributors
- Slightly more boilerplate for interfaces and DI
- High testability, module replaceability, and long-term maintainability
- Must update ADRs whenever architecture changes (PROJECT_RULES Rule 1)
