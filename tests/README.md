# Tests

## Purpose

Comprehensive test suite organized by type and layer. Follows testing pyramid: unit > integration > e2e > contract.

## Responsibilities

- Unit tests (isolated, fast)
- Integration tests (database, external services)
- End-to-end tests (full workflows)
- Contract tests (API schemas)
- Performance tests
- Chaos engineering experiments

## What Belongs Here

- `unit/` - Unit tests by module
- `integration/` - Integration tests
- `e2e/` - End-to-end tests
- `contract/` - API contract tests
- `performance/` - Load/stress tests
- `chaos/` - Chaos experiments
- `fixtures/` - Test data factories
- `conftest.py` - Pytest configuration

## What Must NEVER Belong Here

- Production code
- Test infrastructure as code (use deployment/)

## Dependencies

- `pytest` + `pytest-asyncio`
- `pytest-cov` - Coverage
- `httpx` - API testing
- `factory-boy` - Test factories
- `faker` - Test data generation

## Future Phases

- All phases: Tests alongside implementation