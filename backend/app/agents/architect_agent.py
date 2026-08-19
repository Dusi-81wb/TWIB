"""Architect Agent implementation.

Converts structured requirements into a high-level, modular technical architecture
design without generating code or executing workflows.
"""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel, Field

from app.agents.base_agent import BaseAgent
from app.agents.exceptions import AgentExecutionError, AgentValidationError
from app.agents.models import (
    AgentCapability,
    AgentMetadata,
    AgentRequest,
    AgentResponse,
    AgentStatus,
)
from app.infrastructure.llm.conversation import Conversation
from app.infrastructure.llm.exceptions import LLMProviderError
from app.infrastructure.llm.factory import LLMProviderFactory
from app.infrastructure.llm.response import ChatRequest

ARCHITECT_SYSTEM_PROMPT = """You are the TWIB Architect Agent, a principal
system architect. Your responsibility is to convert requirements into a
high-level modular system architecture.

Rules:
1. Focus on modularity, clean separation of concerns, scalability, and security.
2. Do NOT generate implementation code or workflow graphs.
3. Respond ONLY with a valid JSON object matching the following structure:

{
  "system_overview": "High-level overview description",
  "components": ["Component 1 description", "Component 2 description"],
  "services": ["Service 1 description", "Service 2 description"],
  "data_flow": ["Data flow step 1", "Data flow step 2"],
  "api_requirements": ["API requirement 1", "API requirement 2"],
  "database_design": "High-level database schema and storage strategy",
  "external_integrations": ["Integration 1", "Integration 2"],
  "scalability_considerations": ["Point 1", "Point 2"],
  "security_considerations": ["Point 1", "Point 2"],
  "deployment_considerations": ["Point 1", "Point 2"]
}

Do NOT include any text outside the JSON object.
"""


class ArchitectureDesign(BaseModel):
    """Structured technical architecture design produced by the Architect Agent."""

    system_overview: str = Field(..., description="High-level architecture overview.")
    components: list[str] = Field(
        default_factory=list,
        description="System component definitions.",
    )
    services: list[str] = Field(
        default_factory=list,
        description="Core service definitions.",
    )
    data_flow: list[str] = Field(
        default_factory=list,
        description="Data flow sequence steps.",
    )
    api_requirements: list[str] = Field(
        default_factory=list,
        description="API endpoints and interface requirements.",
    )
    database_design: str = Field(
        default="",
        description="High-level database and storage architecture.",
    )
    external_integrations: list[str] = Field(
        default_factory=list,
        description="External third-party service integrations.",
    )
    scalability_considerations: list[str] = Field(
        default_factory=list,
        description="Scalability and performance strategies.",
    )
    security_considerations: list[str] = Field(
        default_factory=list,
        description="Security, auth, and compliance considerations.",
    )
    deployment_considerations: list[str] = Field(
        default_factory=list,
        description="Infrastructure and deployment guidelines.",
    )


class ArchitectAgent(BaseAgent):
    """Architect Agent for technical system design.

    Inherits from :class:`BaseAgent` and uses the LLM Provider Registry to
    generate structured architecture designs.
    """

    def __init__(
        self,
        llm_factory: LLMProviderFactory | None = None,
        default_model: str = "gpt-4o",
        default_provider: str = "openai",
    ) -> None:
        """Initialize ArchitectAgent.

        Args:
            llm_factory: Optional custom LLMProviderFactory.
            default_model: Default model identifier.
            default_provider: Default provider identifier ('openai' or 'ollama').
        """
        super().__init__(llm_factory=llm_factory)
        self._default_model = default_model
        self._default_provider = default_provider

    @property
    def metadata(self) -> AgentMetadata:
        """Return ArchitectAgent metadata declaration."""
        return AgentMetadata(
            id="architect",
            name="Architect Agent",
            description=(
                "Converts requirements into high-level system architecture designs."
            ),
            version="1.0.0",
            capabilities=[AgentCapability.ARCHITECTING],
            supported_models=[self._default_model, "gpt-4o-mini", "llama3"],
        )

    async def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute the Architect Agent to generate a technical architecture design.

        Args:
            request: AgentRequest containing context with ``analysis_result``.

        Returns:
            AgentResponse containing the structured ArchitectureDesign
                dict in ``result``.

        Raises:
            AgentValidationError: If input or output validation fails.
            AgentExecutionError: If LLM call or design generation fails.
        """
        self.validate_input(request)

        provider_name = request.provider or self._default_provider
        model_name = request.model or self._default_model

        try:
            provider = self._llm_factory.get_provider(provider_name)
        except Exception as err:
            raise AgentExecutionError(
                f"Failed to resolve provider '{provider_name}': {err}",
                agent_id=self.metadata.id,
            ) from err

        conv = request.conversation or Conversation()
        if not conv.system_prompt:
            conv.add_system_message(ARCHITECT_SYSTEM_PROMPT)

        prompt_text = self._format_user_prompt(request)
        conv.add_user_message(prompt_text)

        chat_req = ChatRequest(
            model=model_name,
            messages=conv.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens or 2560,
        )

        try:
            chat_res = await provider.complete(chat_req)
            assistant_text = chat_res.message.content
            conv.add_assistant_message(assistant_text)
        except LLMProviderError as err:
            raise AgentExecutionError(
                f"LLM completion failed for ArchitectAgent: {err.message}",
                agent_id=self.metadata.id,
            ) from err
        except Exception as err:
            raise AgentExecutionError(
                f"Unexpected failure during architecture generation: {err}",
                agent_id=self.metadata.id,
            ) from err

        # Parse output into ArchitectureDesign model
        design_dict = self._parse_json_design(assistant_text, default_goal=request.user_prompt)
        try:
            design = ArchitectureDesign.model_validate(design_dict)
        except Exception as err:
            raise AgentValidationError(
                f"LLM output failed ArchitectureDesign validation: {err}",
                agent_id=self.metadata.id,
            ) from err

        response = AgentResponse(
            agent_id=self.metadata.id,
            status=AgentStatus.COMPLETED,
            result=design.model_dump(),
            conversation=conv,
            metadata={
                "model": model_name,
                "provider": provider_name,
                "usage": chat_res.usage.model_dump(),
            },
        )
        self.validate_output(response)
        return response

    def validate_input(self, request: AgentRequest) -> bool:
        """Validate that request contains analysis_result in context."""
        super().validate_input(request)
        ctx = request.context or {}
        analysis_res = (
            ctx.get("analysis_result")
            or ctx.get("analysis")
            or ctx.get("requirements")
            or ctx.get("upstream_dependencies")
        )

        if not analysis_res:
            raise AgentValidationError(
                "ArchitectAgent requires 'analysis_result' in context",
                agent_id=self.metadata.id,
            )
        return True

    def validate_output(self, response: AgentResponse) -> bool:
        """Validate that response contains a valid ArchitectureDesign result dict."""
        super().validate_output(response)
        if not response.result or not isinstance(response.result, dict):
            raise AgentValidationError(
                "Architect result must be a structured dictionary",
                agent_id=self.metadata.id,
            )
        if (
            "system_overview" not in response.result
            or "components" not in response.result
        ):
            raise AgentValidationError(
                "Architect result missing required 'system_overview' or 'components'",
                agent_id=self.metadata.id,
            )
        return True

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _format_user_prompt(request: AgentRequest) -> str:
        """Format request analysis context into prompt string."""
        ctx = request.context or {}
        analysis = (
            ctx.get("analysis_result")
            or ctx.get("analysis")
            or ctx.get("requirements")
            or ctx.get("upstream_dependencies")
        )

        parts = [f"Instruction: {request.user_prompt}"]
        if analysis:
            parts.append(f"Analysis Requirements:\n{json.dumps(analysis, indent=2, default=str)}")
        return "\n\n".join(parts)

    @staticmethod
    def _normalize_design_dict(data: dict[str, Any], default_goal: str) -> dict[str, Any]:
        def item_to_str(val: Any) -> str:
            if isinstance(val, dict):
                name = val.get("name") or val.get("title") or "Component"
                desc = val.get("description") or val.get("responsibility") or ""
                return f"{name}: {desc}".strip(": ")
            return str(val)

        def flatten_to_strings(val: Any) -> list[str]:
            if not isinstance(val, list):
                return [item_to_str(val)] if val else []
            res: list[str] = []
            for item in val:
                if isinstance(item, list):
                    res.extend([item_to_str(x) for x in item if x])
                elif item:
                    res.append(item_to_str(item))
            return res

        res = dict(data)
        res["system_overview"] = str(res.get("system_overview") or default_goal)
        res["components"] = flatten_to_strings(res.get("components")) or ["Core Execution Engine"]
        res["services"] = flatten_to_strings(res.get("services")) or ["Workflow Service"]
        res["data_flow"] = flatten_to_strings(res.get("data_flow")) or ["Input -> Processing -> Output"]
        res["api_requirements"] = flatten_to_strings(res.get("api_requirements"))
        res["database_design"] = str(res.get("database_design") or "Relational metadata store")
        res["external_integrations"] = flatten_to_strings(res.get("external_integrations"))
        res["scalability_considerations"] = flatten_to_strings(res.get("scalability_considerations"))
        res["security_considerations"] = flatten_to_strings(res.get("security_considerations"))
        res["deployment_considerations"] = flatten_to_strings(res.get("deployment_considerations"))
        return res

    def _parse_json_design(self, text: str, default_goal: str = "System Architecture") -> dict[str, Any]:
        """Parse raw LLM response text into a JSON design dictionary."""
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```$", "", cleaned)
            cleaned = cleaned.strip()

        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict):
                return self._normalize_design_dict(parsed, default_goal)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                    if isinstance(parsed, dict):
                        return self._normalize_design_dict(parsed, default_goal)
                except json.JSONDecodeError:
                    pass

        return {
            "system_overview": cleaned[:300] if cleaned else default_goal,
            "components": ["System Architecture Node: Handle structured workflow requirements"],
            "services": ["Workflow Execution Service"],
            "data_flow": ["Upstream Context -> System Component -> Output Synthesis"],
            "api_requirements": ["REST API", "Event Dispatcher"],
            "database_design": "Relational database with transactional support",
            "external_integrations": ["LLM Provider Gateway"],
            "scalability_considerations": ["Stateless Execution", "Asynchronous Processing"],
            "security_considerations": ["Authentication and Request Validation"],
            "deployment_considerations": ["Containerized Deployment"],
        }
