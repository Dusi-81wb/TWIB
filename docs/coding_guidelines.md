# TWIB Coding Guidelines

## Overview

This document establishes mandatory coding standards for all contributors to TWIB. These standards ensure consistency, maintainability, and quality across the entire codebase.

## General Principles

### Code Quality
- **Readability over cleverness** - Code is read more than written
- **Explicit over implicit** - Clear intent, no magic
- **Consistency over preference** - Follow the standard, not personal style
- **Fail fast** - Validate early, crash early, recover gracefully

### Architecture Compliance
- **Clean Architecture layers** - Never violate dependency direction
- **Single responsibility** - One reason to change per module/class/function
- **Dependency injection** - No hardcoded dependencies
- **Interface segregation** - Small, focused protocols

---

## Naming Conventions

### Files and Directories
```python
# Directories: snake_case
app/services/workflow/generation.py

# Python files: snake_case.py
user_service.py
workflow_executor.py

# Test files: test_*.py
test_user_service.py
test_workflow_generation.py

# Config files: descriptive names
docker-compose.yml
pyproject.toml
.mypy.ini
```

### Classes and Types
```python
# Classes: PascalCase
class UserService:
    pass

class WorkflowExecutor:
    pass

# Protocols/Interfaces: PascalCase, often with suffix
class UserRepository(Protocol):
    pass

class LLMProvider(Protocol):
    pass

# Type variables: PascalCase with T prefix
T = TypeVar("T")
TUser = TypeVar("TUser", bound=User)
```

### Functions and Methods
```python
# Functions: snake_case
async def get_user_by_id(user_id: UserId) -> User | None:
    pass

async def create_workflow_from_template(template_id: TemplateId) -> Workflow:
    pass

# Private: leading underscore
async def _validate_workflow_structure(graph: WorkflowGraph) -> ValidationResult:
    pass

# Properties: snake_case
@property
def is_active(self) -> bool:
    pass
```

### Constants and Enums
```python
# Module constants: UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT_SECONDS = 30
MAX_CONTEXT_TOKENS = 128_000

# Enums: PascalCase class, UPPER_SNAKE_CASE members
class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
```

### Variables
```python
# Variables: snake_case
user_id = UserId("123")
workflow_graph = WorkflowGraph()
llm_provider = OpenAIProvider()

# Private module-level: leading underscore
_default_timeout = 30
```

---

## Type Hints

### Mandatory Requirements
- **All public functions/methods** must have type hints
- **Return types** always annotated
- **No `Any`** unless absolutely necessary (with comment)
- **Use `typing` imports** for complex types

### Preferred Patterns
```python
# Good: Explicit types
async def get_users(
    limit: int = 50,
    offset: int = 0,
    filters: UserFilters | None = None,
) -> list[User]:
    ...

# Good: Protocols for dependencies
class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

# Good: Union with |
async def process(data: str | bytes) -> Result:
    ...

# Good: Generic types
class Repository(Generic[T]):
    async def get(self, id: ID) -> T | None: ...

# Avoid: Any without justification
def legacy_function(data: Any) -> Any:  # TODO: Remove Any
    ...
```

### Import Style
```python
# Standard library first
from collections.abc import Sequence
from datetime import datetime
from typing import Protocol, TypeVar

# Third-party second
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

# Local third
from app.schemas.user import UserCreate, UserResponse
from app.repositories.protocols.repository import UserRepository
```

---

## Async Conventions

### Rules
- **All I/O operations MUST be async**
- Use `async def` for all service methods, repository methods, API handlers
- **Never block the event loop** - no `time.sleep`, `requests.get`, etc.
- Use `asyncio.sleep` for delays
- Use `async with` for context managers
- Prefer `asyncio.gather` for concurrent operations

### Patterns
```python
# Good: Concurrent execution
async def fetch_user_data(user_ids: list[UserId]) -> list[User]:
    tasks = [self._repo.get_by_id(uid) for uid in user_ids]
    return await asyncio.gather(*tasks)

# Good: Async context manager
async with self._db.transaction() as tx:
    await self._repo.save(user, tx)

# Good: Timeout handling
async def call_llm_with_timeout(messages: list[Message]) -> Completion:
    try:
        return await asyncio.wait_for(
            self._llm.complete(messages),
            timeout=LLM_TIMEOUT_SECONDS,
        )
    except TimeoutError:
        raise LLMTimeoutError("LLM request timed out")

# Avoid: Blocking calls
# BAD: time.sleep(1)
# BAD: requests.post(url, json=data)
# BAD: synchronous file I/O
```

---

## Error Handling

### Exception Hierarchy
```python
# Base exceptions in app/core/exceptions/
class TWIBError(Exception):
    """Base application error."""
    def __init__(
        self,
        message: str,
        code: str,
        details: dict | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.details = details or {}

class DomainError(TWIBError):
    """Business rule violation."""
    pass

class NotFoundError(TWIBError):
    """Resource not found."""
    pass

class ValidationError(TWIBError):
    """Input validation failed."""
    pass

class InfrastructureError(TWIBError):
    """External system failure."""
    pass
```

### Handling Patterns
```python
# Good: Specific exception handling
async def get_user(user_id: UserId) -> User:
    user = await self._repo.get_by_id(user_id)
    if user is None:
        raise NotFoundError(
            message=f"User {user_id} not found",
            code="USER_NOT_FOUND",
            details={"user_id": str(user_id)},
        )
    return user

# Good: Exception chaining
try:
    await self._external_api.call()
except ExternalAPIError as e:
    raise InfrastructureError(
        message="Failed to call external API",
        code="EXTERNAL_API_FAILURE",
    ) from e

# Good: Structured error responses
@app.exception_handler(TWIBError)
async def twib_error_handler(request: Request, exc: TWIBError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.http_status,
        content=ErrorResponse(
            error=exc.code,
            message=exc.message,
            details=exc.details,
        ).model_dump(),
    )

# Avoid: Bare except
# BAD: except Exception:
# BAD: except:
```

---

## Dependency Injection

### Container Registration
```python
# app/container.py
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    # Repositories (singleton - stateless)
    user_repo = providers.Singleton(
        SQLUserRepository,
        session_factory=db.provided.session_factory,
    )
    
    # Services (singleton - stateless)
    user_service = providers.Singleton(
        UserService,
        repo=user_repo,
        event_bus=event_bus,
    )
    
    # Request-scoped (stateful)
    request_context = providers.Factory(RequestContext)
```

### Protocol Definition
```python
# app/repositories/protocols/repository.py
from typing import Protocol
from app.domain.user import User, UserId

class UserRepository(Protocol):
    async def get_by_id(self, id: UserId) -> User | None: ...
    async def get_by_email(self, email: Email) -> User | None: ...
    async def save(self, user: User) -> None: ...
    async def delete(self, id: UserId) -> None: ...
```

### Service Usage
```python
# app/services/user/service.py
class UserService:
    def __init__(
        self,
        repo: UserRepository,
        event_bus: EventBus,
    ) -> None:
        self._repo = repo
        self._event_bus = event_bus
    
    async def create_user(self, data: UserCreate) -> User:
        user = User.create(data)
        await self._repo.save(user)
        await self._event_bus.publish(UserCreated(user.id))
        return user
```

---

## Repository Pattern

### Base Repository
```python
# database/repositories/base.py
from typing import Generic, TypeVar
from abc import ABC, abstractmethod

T = TypeVar("T")
ID = TypeVar("ID")

class Repository(ABC, Generic[T, ID]):
    @abstractmethod
    async def get_by_id(self, id: ID) -> T | None: ...
    
    @abstractmethod
    async def save(self, entity: T) -> None: ...
    
    @abstractmethod
    async def delete(self, id: ID) -> None: ...
    
    @abstractmethod
    async def list(
        self,
        limit: int = 50,
        offset: int = 0,
        filters: dict | None = None,
    ) -> list[T]: ...
```

### Implementation
```python
# database/repositories/user.py
class SQLUserRepository(Repository[User, UserId]):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
    
    async def get_by_id(self, id: UserId) -> User | None:
        async with self._session_factory() as session:
            result = await session.get(UserModel, id.value)
            return self._to_domain(result) if result else None
    
    async def save(self, user: User) -> None:
        async with self._session_factory() as session:
            model = self._to_model(user)
            await session.merge(model)
            await session.commit()
```

---

## Service Pattern

### Base Service
```python
# app/services/base.py
from abc import ABC

class BaseService(ABC):
    """Base class for all services. Stateless, singleton-scoped."""
    pass
```

### Service Implementation
```python
# app/services/workflow/generation.py
class WorkflowGenerationService(BaseService):
    def __init__(
        self,
        planner: PlannerAgent,
        analyst: AnalystAgent,
        architect: ArchitectAgent,
        validator: ValidatorAgent,
        optimizer: OptimizerAgent,
        researcher: ResearcherAgent,
        documentation: DocumentationAgent,
        supervisor: SupervisorAgent,
        repo: WorkflowRepository,
        event_bus: EventBus,
    ) -> None:
        self._planner = planner
        self._analyst = analyst
        # ... all agents
        self._repo = repo
        self._event_bus = event_bus
    
    async def generate(self, request: GenerateWorkflowRequest) -> Workflow:
        # Orchestrate agents
        plan = await self._planner.plan(request.goal)
        requirements = await self._analyst.analyze(plan)
        architecture = await self._architect.design(requirements)
        # ... continue orchestration
        workflow = await self._supervisor.orchestrate(all_results)
        
        await self._repo.save(workflow)
        await self._event_bus.publish(WorkflowCreated(workflow.id))
        return workflow
```

---

## Docstrings

### Google Style (Mandatory)
```python
async def generate_workflow(
    self,
    goal: str,
    context: WorkflowContext | None = None,
) -> Workflow:
    """Generate a workflow from a high-level goal.

    Args:
        goal: Natural language description of the desired workflow.
        context: Optional contextual information (organization, constraints).

    Returns:
        The generated workflow with all nodes, edges, and metadata.

    Raises:
        ValidationError: If goal is empty or invalid.
        LLMError: If agent LLM calls fail.
        WorkflowGenerationError: If orchestration fails.

    Example:
        >>> workflow = await service.generate_workflow(
        ...     goal="Create approval workflow for expense reports",
        ...     context=WorkflowContext(org_id=OrgId("123"))
        ... )
    """
```

### Class Docstrings
```python
class WorkflowGenerationService(BaseService):
    """Orchestrates multi-agent workflow generation.

    This service coordinates the Planner, Analyst, Architect, Validator,
    Optimizer, Researcher, Documentation, and Supervisor agents to
    transform a high-level goal into an executable workflow.

    Attributes:
        _planner: Agent for task decomposition.
        _analyst: Agent for requirements analysis.
        _architect: Agent for technical architecture.
        _validator: Agent for output validation.
        _optimizer: Agent for workflow optimization.
        _researcher: Agent for external research.
        _documentation: Agent for auto-documentation.
        _supervisor: Agent for multi-agent orchestration.
        _repo: Repository for workflow persistence.
        _event_bus: Event bus for domain events.
    """
```

---

## Logging

### Structured Logging
```python
import structlog

logger = structlog.get_logger(__name__)

async def create_workflow(self, data: WorkflowCreate) -> Workflow:
    logger.info(
        "workflow_creation_started",
        user_id=str(data.user_id),
        template_id=str(data.template_id) if data.template_id else None,
    )
    
    try:
        workflow = await self._do_create(data)
        logger.info(
            "workflow_created",
            workflow_id=str(workflow.id),
            user_id=str(data.user_id),
        )
        return workflow
    except ValidationError as e:
        logger.warning(
            "workflow_creation_validation_failed",
            user_id=str(data.user_id),
            error_code=e.code,
            error_details=e.details,
        )
        raise
    except Exception as e:
        logger.exception(
            "workflow_creation_failed",
            user_id=str(data.user_id),
            error_type=type(e).__name__,
        )
        raise
```

### Log Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: General operational events (start/end, key decisions)
- **WARNING**: Unexpected but handled (validation failures, retries)
- **ERROR**: Unhandled failures requiring attention
- **CRITICAL**: System-threatening issues

---

## Testing Standards

### Unit Test Structure
```python
# backend/tests/unit/test_services/test_workflow_generation.py
import pytest
from unittest.mock import AsyncMock, Mock

from app.services.workflow.generation import WorkflowGenerationService
from agents.planner import PlannerAgent
# ... other agents

class TestWorkflowGenerationService:
    @pytest.fixture
    def planner(self) -> PlannerAgent:
        return AsyncMock(spec=PlannerAgent)
    
    @pytest.fixture
    def service(self, planner, analyst, architect, validator, optimizer, 
                researcher, documentation, supervisor, repo, event_bus) -> WorkflowGenerationService:
        return WorkflowGenerationService(
            planner=planner,
            analyst=analyst,
            architect=architect,
            validator=validator,
            optimizer=optimizer,
            researcher=researcher,
            documentation=documentation,
            supervisor=supervisor,
            repo=repo,
            event_bus=event_bus,
        )
    
    async def test_generate_workflow_calls_all_agents(
        self,
        service: WorkflowGenerationService,
        planner: PlannerAgent,
        # ... other mocks
    ) -> None:
        # Arrange
        request = GenerateWorkflowRequest(goal="Test goal")
        planner.plan.return_value = TaskGraph()
        # ... setup other mocks
        
        # Act
        result = await service.generate(request)
        
        # Assert
        planner.plan.assert_awaited_once_with(request.goal)
        analyst.analyze.assert_awaited_once()
        # ... verify all agents called
        assert isinstance(result, Workflow)
```

### Integration Test Patterns
```python
# backend/tests/integration/test_database/test_user_repo.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories.user import SQLUserRepository
from database.models.user import UserModel

class TestSQLUserRepository:
    async def test_save_and_get_user(
        self,
        session: AsyncSession,
        user_repo: SQLUserRepository,
    ) -> None:
        # Arrange
        user = User.create(UserCreate(email="test@example.com", name="Test"))
        
        # Act
        await user_repo.save(user)
        retrieved = await user_repo.get_by_id(user.id)
        
        # Assert
        assert retrieved is not None
        assert retrieved.email == user.email
        assert retrieved.name == user.name
```

---

## Git Practices

### Commit Messages (Conventional Commits)
```
feat(workflow): add parallel node execution support

Add ParallelNode type and scheduler support for concurrent
branch execution. Includes timeout and error handling.

Closes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`

### Branch Naming
```
feature/workflow-parallel-nodes
fix/agent-memory-leak
docs/api-documentation
refactor/repository-base-class
```

---

## Code Review Checklist

Before submitting PR, verify:

- [ ] Follows all naming conventions
- [ ] Type hints on all public APIs
- [ ] Google-style docstrings on all public classes/methods
- [ ] No bare `except:` or `except Exception:`
- [ ] Proper async/await usage (no blocking calls)
- [ ] Dependency injection used (no direct instantiation)
- [ ] Repository pattern followed (no raw SQL in services)
- [ ] Service pattern followed (no business logic in API/routes)
- [ ] Custom exceptions used (no generic exceptions)
- [ ] Structured logging with correlation IDs
- [ ] Unit tests for new logic (>80% coverage)
- [ ] Integration tests for database/external calls
- [ ] No circular imports
- [ ] Lint passes (`ruff check .`)
- [ ] Typecheck passes (`mypy .`)
- [ ] Tests pass (`pytest`)