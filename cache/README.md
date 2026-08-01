# Cache

## Purpose

Caching layer using Redis/Valkey for high-performance data access, session storage, rate limiting, and pub/sub messaging.

## Responsibilities

- Cache client management
- Key namespacing
- TTL strategies
- Cache invalidation patterns
- Distributed locking
- Pub/Sub for real-time
- Stream processing

## What Belongs Here

- Redis client wrapper
- Cache service (get/set/delete)
- Decorators for caching
- Lock utilities
- Stream consumers

## What Must NEVER Belong Here

- Business logic
- Database operations
- LLM calls

## Dependencies

- `redis` / `valkey-py`
- `backend.config` - Redis URL

## Future Phases

- Phase 1: Cache infrastructure
- Phase 10: Pub/Sub for realtime