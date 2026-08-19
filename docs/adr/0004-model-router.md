# ADR-0004 Model Router

## Status

Accepted

## Context

TWIB is AI-native and supports multiple LLM providers simultaneously. Application services and agents must never depend on a specific model or provider. The platform needs a single point that selects models based on cost, latency, capability, and availability, with failover.

## Decision

Introduce a Model Router layer between the Context Manager and LLM providers.

- Application Services and agents never reference specific models
- Router selects provider/model per request based on cost, latency, capability, availability, token limit, and streaming support
- Router handles retry and failover when a provider is unavailable
- Every provider implements the same `LLMProvider` interface
- Providers are registered as replaceable adapters

## Alternatives Considered

- Direct per-provider calls from agents: rejected, creates tight coupling (PROJECT_RULES Rule 7)
- Single fixed provider: rejected, no cost/latency optimization or failover
- External LLM gateway service: rejected, added operational complexity for current scale

## Consequences

- Centralized routing and cost optimization
- Transparent provider failover
- Requires accurate model capability metadata and routing analytics
- Providers remain independently replaceable without touching business logic
