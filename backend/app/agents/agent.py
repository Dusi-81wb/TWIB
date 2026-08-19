"""Agent Core module.

Re-exports the primary :class:`~app.agents.base_agent.BaseAgent` class and core
agent abstractions for simple importing from ``app.agents.agent``.
"""

from app.agents.base_agent import BaseAgent

__all__ = ["BaseAgent"]
