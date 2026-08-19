# Analytics

## Purpose

Analytics and observability platform for tracking usage, performance, costs, and business metrics across the platform.

## Responsibilities

- Event tracking pipeline
- Metric aggregation
- Dashboard data APIs
- Custom report generation
- Export functionality
- Alerting rules
- Cost attribution

## What Belongs Here

- Event collector
- Aggregation workers
- Query API
- Report builders
- Alert evaluator

## What Must NEVER Belong Here

- Business logic (use services/)
- Raw data storage (use database/vector_db)
- Frontend dashboards (use frontend/)

## Dependencies

- `database.repositories` - Metric storage
- `cache` - Real-time counters
- `llm.router` - Cost tracking
- `workflows.executor` - Execution metrics

## Future Phases

- Phase 12: Analytics implementation