"""Agent Core framework package.

Exposes base agent abstractions, models, capabilities, and exceptions for TWIB:

- :class:`.BaseAgent`: Abstract base class for all AI agents.
- :class:`.AgentCapability`: Enumeration of agent capability types.
- :class:`.AgentStatus`: Enumeration of agent execution states.
- :class:`.AgentMetadata`: Metadata schema describing agent capabilities.
- :class:`.AgentRequest`: Execution request payload.
- :class:`.AgentResponse`: Execution response payload.
- :class:`.AgentError`: Base exception for agent errors.
- :class:`.AgentExecutionError`: Exception raised on execution failure.
- :class:`.AgentValidationError`: Exception raised on validation failure.
- :class:`.AgentNotFoundError`: Exception raised when an agent is not found.
"""

from app.agents.agent import BaseAgent
from app.agents.analyst_agent import (
    AnalystAgent,
    RequirementsAnalysis,
)
from app.agents.architect_agent import (
    ArchitectAgent,
    ArchitectureDesign,
)
from app.agents.documentation_agent import (
    DocSection,
    DocType,
    DocumentationAgent,
    DocumentationOutput,
)
from app.agents.exceptions import (
    AgentError,
    AgentExecutionError,
    AgentNotFoundError,
    AgentValidationError,
)
from app.agents.models import (
    AgentCapability,
    AgentMetadata,
    AgentRequest,
    AgentResponse,
    AgentStatus,
)
from app.agents.optimizer_agent import (
    OptimizationResult,
    OptimizerAgent,
)
from app.agents.planner_agent import (
    ExecutionPlan,
    PlannerAgent,
    RequiredTask,
    TaskDependency,
)
from app.agents.research_agent import (
    ResearchAgent,
    ResearchReport,
)
from app.agents.supervisor_agent import (
    AgentExecutionStep,
    SupervisorAgent,
    SupervisorResult,
)
from app.agents.validator_agent import (
    ValidationReport,
    ValidationStatus,
    ValidatorAgent,
)

__all__ = [
    "AgentCapability",
    "AgentError",
    "AgentExecutionError",
    "AgentExecutionStep",
    "AgentMetadata",
    "AgentNotFoundError",
    "AgentRequest",
    "AgentResponse",
    "AgentStatus",
    "AgentValidationError",
    "AnalystAgent",
    "ArchitectAgent",
    "ArchitectureDesign",
    "BaseAgent",
    "DocSection",
    "DocType",
    "DocumentationAgent",
    "DocumentationOutput",
    "ExecutionPlan",
    "OptimizationResult",
    "OptimizerAgent",
    "PlannerAgent",
    "RequiredTask",
    "RequirementsAnalysis",
    "ResearchAgent",
    "ResearchReport",
    "SupervisorAgent",
    "SupervisorResult",
    "TaskDependency",
    "ValidationReport",
    "ValidationStatus",
    "ValidatorAgent",
]
