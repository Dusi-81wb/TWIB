"""Research Agent implementation.

Gathers, synthesizes, and summarizes information for a research topic or objective
into structured responses backed by an LLM Gateway.
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
from app.infrastructure.llm.gateway import LLMGateway
from app.infrastructure.llm.message import ChatMessage, MessageRole
from app.infrastructure.llm.models import GatewayResponse
from app.infrastructure.llm.response import ChatRequest

RESEARCHER_SYSTEM_PROMPT = r"""You are the TWIB Research Agent, an expert assistant.
Your goal is to provide clear, accurate, and insightful explanations and analysis.

Behavior Guidelines:
1. Answer the actual question directly and accurately.
2. Be concise by default; expand when the depth of the question requires it.
3. Do NOT force every answer into rigid templates (such as Summary, Key Findings,
   Best Practices, Risks, References). Only include headings when useful.
4. Do NOT generate Python or code snippets unless:
   - The user explicitly asks for code (e.g., "with Python", "write code").
   - Code is strictly necessary to demonstrate the concept.
   - A concrete technical implementation is requested.
5. Do NOT claim to have performed live web searches or fabricate citations/sources
   unless tools were executed. Say "Based on available knowledge..." when discussing.
6. Maintain conversational context across turns. Seamlessly understand follow-up
   questions (such as "What are the main types?", "Which one does Android use?").
7. Admit uncertainty when necessary rather than speculating.

Formatting:
- Respond in clean, beautifully rendered GitHub-flavored Markdown.
- NEVER return raw JSON objects or wrap responses in JSON strings.
- Use bullet lists, bold text, markdown tables, and headings naturally.
"""


class ResearchReport(BaseModel):
    """Structured research report produced by the Research Agent."""

    topic: str = Field(..., description="Research topic string.")
    summary: str = Field(..., description="Executive summary of research.")
    key_findings: list[str] = Field(
        default_factory=list,
        description="Key findings and facts.",
    )
    best_practices: list[str] = Field(
        default_factory=list,
        description="Recommended industry best practices.",
    )
    risks: list[str] = Field(
        default_factory=list,
        description="Identified risks and concerns.",
    )
    references: list[str] = Field(
        default_factory=list,
        description="Relevant references or documentation sources.",
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="Actionable recommendations.",
    )


class ResearchAgent(BaseAgent):
    """Research Agent for domain research and factual knowledge synthesis.

    Inherits from :class:`BaseAgent` and uses an injected :class:`LLMGateway`
    (backed by OmniRoute) to generate real research responses.
    """

    def __init__(
        self,
        llm_gateway: LLMGateway | None = None,
        llm_factory: LLMProviderFactory | None = None,
        default_model: str | None = None,
        default_provider: str = "omniroute",
    ) -> None:
        """Initialize ResearchAgent.

        Args:
            llm_gateway: Injected LLMGateway dependency (e.g. OmniRouteGateway).
            llm_factory: Optional custom LLMProviderFactory for legacy providers.
            default_model: Default model identifier (or None to dynamically resolve).
            default_provider: Default provider identifier ('omniroute').
        """
        super().__init__(llm_factory=llm_factory)
        self._llm_gateway = llm_gateway
        self._default_model = default_model
        self._default_provider = default_provider

    @property
    def metadata(self) -> AgentMetadata:
        """Return ResearchAgent metadata declaration."""
        return AgentMetadata(
            id="researcher",
            name="Research Agent",
            description=(
                "Gathers and synthesizes factual information into research reports."
            ),
            version="1.0.0",
            capabilities=[AgentCapability.RESEARCH],
            supported_models=[self._default_model or "default", "gpt-4o", "llama3"],
        )

    async def run(
        self,
        prompt: str,
        *,
        temperature: float = 0.3,
        model: str | None = None,
    ) -> GatewayResponse:
        """Run ResearchAgent synchronously against LLMGateway.

        Args:
            prompt: User prompt / research question string.
            temperature: Sampling temperature (0.0 to 2.0).
            model: Target model identifier override.

        Returns:
            TWIB-specific GatewayResponse object with Markdown answer.

        Raises:
            AgentValidationError: If prompt is empty or whitespace.
            AgentExecutionError: If gateway execution fails.
        """
        if not prompt or not prompt.strip():
            raise AgentValidationError(
                "Prompt must be a non-empty string.",
                agent_id=self.metadata.id,
            )

        target_model = model or self._default_model
        user_msg = ChatMessage(role=MessageRole.USER, content=prompt.strip())

        if not self._llm_gateway:
            from app.infrastructure.llm.omniroute_gateway import OmniRouteGateway

            self._llm_gateway = OmniRouteGateway()

        try:
            return await self._llm_gateway.chat(
                [user_msg],
                model=target_model,
                temperature=temperature,
                system_prompt=RESEARCHER_SYSTEM_PROMPT,
            )
        except Exception as err:
            raise AgentExecutionError(
                f"ResearchAgent gateway execution failed: {err}",
                agent_id=self.metadata.id,
            ) from err

    async def run_conversation(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.3,
        model: str | None = None,
    ) -> GatewayResponse:
        """Run ResearchAgent over a multi-turn conversation list against LLMGateway.

        Args:
            messages: List of ChatMessage objects (user/assistant turns).
            temperature: Sampling temperature (0.0 to 2.0).
            model: Target model identifier override.

        Returns:
            TWIB-specific GatewayResponse object containing assistant answer.

        Raises:
            AgentValidationError: If message list is empty.
            AgentExecutionError: If gateway execution fails.
        """
        if not messages:
            raise AgentValidationError(
                "Conversation messages list cannot be empty.",
                agent_id=self.metadata.id,
            )

        target_model = model or self._default_model

        if not self._llm_gateway:
            from app.infrastructure.llm.omniroute_gateway import OmniRouteGateway

            self._llm_gateway = OmniRouteGateway()

        try:
            return await self._llm_gateway.chat(
                messages,
                model=target_model,
                temperature=temperature,
                system_prompt=RESEARCHER_SYSTEM_PROMPT,
            )
        except Exception as err:
            raise AgentExecutionError(
                f"ResearchAgent gateway execution failed: {err}",
                agent_id=self.metadata.id,
            ) from err

    async def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute the Research Agent to generate a research report.

        Args:
            request: AgentRequest containing user_prompt, context, and settings.

        Returns:
            AgentResponse containing ResearchReport dictionary.

        Raises:
            AgentValidationError: If input validation fails.
            AgentExecutionError: If LLM call fails.
        """
        self.validate_input(request)

        provider_name = request.provider or self._default_provider
        model_name = request.model or self._default_model or "default"
        conv = request.conversation or Conversation()

        prompt_text = self._format_user_prompt(request)
        conv.add_user_message(prompt_text)

        assistant_text = ""
        usage_dict: dict[str, Any] = {}

        # If explicit provider requested or gateway not provided, use LLMProviderFactory
        if request.provider or not self._llm_gateway:
            try:
                provider = self._llm_factory.get_provider(provider_name)
                chat_req = ChatRequest(
                    model=model_name,
                    messages=conv.messages,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens or 2048,
                )
                chat_res = await provider.complete(chat_req)
                assistant_text = chat_res.message.content
                conv.add_assistant_message(assistant_text)
                usage_dict = chat_res.usage.model_dump()
            except LLMProviderError as err:
                raise AgentExecutionError(
                    f"LLM completion failed for ResearchAgent: {err.message}",
                    agent_id=self.metadata.id,
                ) from err
            except Exception as err:
                raise AgentExecutionError(
                    f"ResearchAgent execution failed for provider '{provider_name}': "
                    f"{err}",
                    agent_id=self.metadata.id,
                ) from err
        else:
            try:
                gw_res = await self._llm_gateway.chat(
                    conv.messages,
                    model=model_name,
                    temperature=request.temperature or 0.3,
                    system_prompt=RESEARCHER_SYSTEM_PROMPT,
                )
                assistant_text = gw_res.answer
                conv.add_assistant_message(assistant_text)
                usage_dict = gw_res.usage.model_dump()
            except Exception as err:
                raise AgentExecutionError(
                    f"LLM Gateway execution failed for ResearchAgent: {err}",
                    agent_id=self.metadata.id,
                ) from err

        # Parse output into ResearchReport model
        report_dict = self._parse_json_report(assistant_text, default_topic=request.user_prompt or "Research Analysis")
        try:
            report = ResearchReport.model_validate(report_dict)
        except Exception as err:
            raise AgentValidationError(
                f"LLM output failed ResearchReport validation: {err}",
                agent_id=self.metadata.id,
            ) from err

        response = AgentResponse(
            agent_id=self.metadata.id,
            status=AgentStatus.COMPLETED,
            result=report.model_dump(),
            conversation=conv,
            metadata={
                "model": model_name,
                "provider": provider_name,
                "usage": usage_dict,
            },
        )
        self.validate_output(response)
        return response

    def validate_input(self, request: AgentRequest) -> bool:
        """Validate that request contains a non-empty user prompt / research topic."""
        super().validate_input(request)
        if len(request.user_prompt.strip()) < 3:
            raise AgentValidationError(
                "Research topic is too short to execute research",
                agent_id=self.metadata.id,
            )
        return True

    def validate_output(self, response: AgentResponse) -> bool:
        """Validate that response contains a non-empty result."""
        super().validate_output(response)
        if not response.result or not isinstance(response.result, dict):
            raise AgentValidationError(
                "Research result must be a structured dictionary",
                agent_id=self.metadata.id,
            )
        if "topic" not in response.result or "summary" not in response.result:
            raise AgentValidationError(
                "Research result missing required 'topic' or 'summary' keys",
                agent_id=self.metadata.id,
            )
        return True

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _format_user_prompt(request: AgentRequest) -> str:
        """Format request user_prompt (topic) and context into prompt string."""
        parts = [f"Research Topic: {request.user_prompt}"]
        if request.context:
            parts.append(f"Context & Constraints: {json.dumps(request.context)}")
        return "\n\n".join(parts)

    def _parse_json_report(self, text: str, default_topic: str = "Research Analysis") -> dict[str, Any]:
        """Parse raw LLM response text into a report dictionary.

        Attempts to parse JSON first for legacy structured calls; if non-JSON markdown
        or natural text is returned, wraps into a valid ResearchReport dictionary.
        """
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```$", "", cleaned)
            cleaned = cleaned.strip()

        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict) and "summary" in parsed:
                return parsed
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                    if isinstance(parsed, dict) and "summary" in parsed:
                        return parsed
                except json.JSONDecodeError:
                    pass

        if "#" in cleaned or "**" in cleaned or "\n-" in cleaned or "\n*" in cleaned or len(cleaned) > 100:
            return {
                "topic": default_topic,
                "summary": cleaned,
                "key_findings": ["Domain research completed via LLM Gateway."],
                "best_practices": [],
                "risks": [],
                "references": [],
                "recommendations": [],
            }

        raise AgentValidationError(
            f"Failed to parse structured research JSON from LLM response: {text[:200]}...",
            agent_id=self.metadata.id,
        )
