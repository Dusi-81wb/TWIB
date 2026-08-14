"""Documentation Agent implementation.

Transforms validated and optimized outputs into professional markdown documentation
(READMEs, Technical Specs, API Docs, User Guides, etc.) without fabricating information.
"""

from __future__ import annotations

import json
import re
from enum import StrEnum
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
from app.core.logging import get_logger
from app.infrastructure.llm.conversation import Conversation
from app.infrastructure.llm.exceptions import LLMProviderError
from app.infrastructure.llm.factory import LLMProviderFactory
from app.infrastructure.llm.response import ChatRequest

logger = get_logger(__name__)


DOCUMENTATION_SYSTEM_PROMPT = """You are the TWIB Documentation Agent, a writer.
Your responsibility is to transform provided content into documentation.

Rules:
1. Do NOT fabricate or invent new requirements or architecture details.
2. Structure output cleanly into headings and professional Markdown sections.
3. Respond ONLY with a valid JSON object matching the following structure:

{
  "doc_type": "readme",
  "title": "Document Title",
  "summary": "Brief executive summary",
  "sections": [
    {
      "heading": "Section Heading",
      "content": "Section Markdown content"
    }
  ],
  "markdown_content": "# Full compiled markdown text here"
}

Do NOT include any text outside the JSON object.
"""


class DocType(StrEnum):
    """Supported document types for the Documentation Agent."""

    README = "readme"
    TECHNICAL_SPECIFICATION = "tech_spec"
    API_DOCUMENTATION = "api_doc"
    ARCHITECTURE_DOCUMENT = "architecture_doc"
    USER_GUIDE = "user_guide"
    DEVELOPER_GUIDE = "developer_guide"
    PROJECT_SUMMARY = "project_summary"


class DocSection(BaseModel):
    """Single section within structured documentation."""

    heading: str = Field(..., description="Section title or heading.")
    content: str = Field(..., description="Markdown content for this section.")


class DocumentationOutput(BaseModel):
    """Structured documentation result produced by the Documentation Agent."""

    doc_type: str = Field(..., description="Document type string.")
    title: str = Field(..., description="Document title.")
    summary: str = Field(default="", description="Brief document summary.")
    sections: list[DocSection] = Field(
        default_factory=list,
        description="Structured sections array.",
    )
    markdown_content: str = Field(
        ...,
        description="Compiled full Markdown document string.",
    )


class DocumentationAgent(BaseAgent):
    """Documentation Agent for generating professional markdown documentation.

    Inherits from :class:`BaseAgent` and uses the LLM Provider Registry to
    generate structured documentation across multiple formats.
    """

    def __init__(
        self,
        llm_factory: LLMProviderFactory | None = None,
        default_model: str = "gpt-4o",
        default_provider: str = "openai",
    ) -> None:
        """Initialize DocumentationAgent.

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
        """Return DocumentationAgent metadata declaration."""
        return AgentMetadata(
            id="documentation",
            name="Documentation Agent",
            description=(
                "Transforms optimized content into professional Markdown documentation."
            ),
            version="1.0.0",
            capabilities=[AgentCapability.DOCUMENTATION],
            supported_models=[self._default_model, "gpt-4o-mini", "llama3"],
        )

    async def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute the Documentation Agent to generate structured documentation.

        Args:
            request: AgentRequest containing context with ``optimized_output``
                and ``documentation_type``.

        Returns:
            AgentResponse containing the structured DocumentationOutput
                dict in ``result``.

        Raises:
            AgentValidationError: If input or output validation fails.
            AgentExecutionError: If LLM call or document generation fails.
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
            conv.add_system_message(DOCUMENTATION_SYSTEM_PROMPT)

        prompt_text = self._format_user_prompt(request)
        conv.add_user_message(prompt_text)

        chat_req = ChatRequest(
            model=model_name,
            messages=conv.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens or 3000,
        )

        try:
            chat_res = await provider.complete(chat_req)
            assistant_text = chat_res.message.content
            conv.add_assistant_message(assistant_text)
        except LLMProviderError as err:
            raise AgentExecutionError(
                f"LLM completion failed for DocumentationAgent: {err.message}",
                agent_id=self.metadata.id,
            ) from err
        except Exception as err:
            raise AgentExecutionError(
                f"Unexpected failure during documentation generation: {err}",
                agent_id=self.metadata.id,
            ) from err

        doc_dict = self._parse_json_doc(assistant_text)
        try:
            doc = DocumentationOutput.model_validate(doc_dict)
        except Exception as err:
            raise AgentValidationError(
                f"LLM output failed DocumentationOutput validation: {err}",
                agent_id=self.metadata.id,
            ) from err

        response = AgentResponse(
            agent_id=self.metadata.id,
            status=AgentStatus.COMPLETED,
            result=doc.model_dump(),
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
        """Validate that request contains optimized_output and valid documentation_type.

        Args:
            request: Incoming AgentRequest payload.

        Returns:
            True if valid.

        Raises:
            AgentValidationError: If optimized_output or type is invalid.
        """
        super().validate_input(request)
        ctx = request.context or {}
        opt_out = (
            ctx.get("optimized_output")
            or ctx.get("target_output")
            or ctx.get("input_content")
        )
        doc_type_val = (
            ctx.get("documentation_type") or ctx.get("doc_type") or request.user_prompt
        )

        if not opt_out:
            raise AgentValidationError(
                "DocumentationAgent requires 'optimized_output' in context",
                agent_id=self.metadata.id,
            )

        if not doc_type_val or not str(doc_type_val).strip():
            raise AgentValidationError(
                "DocumentationAgent requires a valid 'documentation_type'",
                agent_id=self.metadata.id,
            )

        # Check if custom doc type string or member of DocType
        supported = {e.value for e in DocType}
        normalized = str(doc_type_val).strip().lower()
        if normalized not in supported and not any(
            k in normalized for k in ["readme", "spec", "doc", "guide", "summary"]
        ):
            raise AgentValidationError(
                f"Unsupported documentation type '{doc_type_val}'. "
                f"Supported types: {sorted(supported)}",
                agent_id=self.metadata.id,
            )

        return True

    def validate_output(self, response: AgentResponse) -> bool:
        """Validate that response contains a valid DocumentationOutput dict.

        Args:
            response: Outgoing AgentResponse payload.

        Returns:
            True if valid.

        Raises:
            AgentValidationError: If result is missing or incomplete.
        """
        super().validate_output(response)
        if not response.result or not isinstance(response.result, dict):
            raise AgentValidationError(
                "Documentation result must be a structured dictionary",
                agent_id=self.metadata.id,
            )
        if "markdown_content" not in response.result or "title" not in response.result:
            raise AgentValidationError(
                "Documentation result missing required 'markdown_content' or 'title'",
                agent_id=self.metadata.id,
            )
        return True

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _format_user_prompt(request: AgentRequest) -> str:
        """Format request content and doc_type into LLM prompt string."""
        ctx = request.context or {}
        opt_out = (
            ctx.get("optimized_output")
            or ctx.get("target_output")
            or ctx.get("input_content")
        )
        doc_type = (
            ctx.get("documentation_type") or ctx.get("doc_type") or request.user_prompt
        )

        parts = [
            f"Target Document Type: {doc_type}",
            f"Instruction / Title: {request.user_prompt}",
            f"Input Optimized Content:\n{json.dumps(opt_out, indent=2)}",
        ]
        return "\n\n".join(parts)

    def _parse_json_doc(self, text: str) -> dict[str, Any]:
        """Parse raw LLM response text into a JSON documentation dictionary.

        Args:
            text: Response text returned by LLM provider.

        Returns:
            Parsed documentation dictionary.

        Raises:
            AgentValidationError: If JSON is malformed or unparseable.
        """
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```$", "", cleaned)
            cleaned = cleaned.strip()

        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                    if isinstance(parsed, dict):
                        return parsed
                except json.JSONDecodeError:
                    logger.warning(
                        "Failed to parse regex match as JSON in DocumentationAgent",
                        exc_info=True,
                    )

        raise AgentValidationError(
            f"Failed to parse documentation JSON from LLM: {text[:150]}...",
            agent_id=self.metadata.id,
        )
