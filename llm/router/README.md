# LLM Router

## Purpose

Intelligent model routing based on task requirements, cost optimization, performance targets, and availability. Implements strategies for model selection.

## Responsibilities

- Routing strategy implementations
- Cost-aware model selection
- Latency-aware routing
- Capability-based matching
- Fallback chains
- A/B testing framework
- Usage analytics

## What Belongs Here

- Router interface
- Strategy implementations
- Model registry
- Decision logging

## What Must NEVER Belong Here

- Provider implementations (use providers/)
- Business logic
- Direct LLM calls

## Dependencies

- `llm.providers` - Provider implementations
- `analytics` - Routing analytics
- `cache` - Routing cache

## Future Phases

- Phase 6: Router implementation