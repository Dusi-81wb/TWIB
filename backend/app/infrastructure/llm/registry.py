"""LLM Provider Registry.

Manages registration and lookup of LLMProvider classes and instances. Allows
registering new providers dynamically without altering business logic.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.infrastructure.llm.exceptions import ProviderError
from app.infrastructure.llm.provider import LLMProvider

if TYPE_CHECKING:  # pragma: no cover
    pass


class LLMProviderRegistry:
    """Registry managing LLM provider implementations.

    Attributes:
        _provider_classes: Mapping of provider names to provider classes.
        _provider_instances: Mapping of provider names to active provider instances.
    """

    def __init__(self) -> None:
        """Initialize empty provider registry."""
        self._provider_classes: dict[str, type[LLMProvider]] = {}
        self._provider_instances: dict[str, LLMProvider] = {}

    def register_class(self, name: str, provider_cls: type[LLMProvider]) -> None:
        """Register an LLMProvider class by name.

        Args:
            name: Normalized provider name (e.g. 'openai').
            provider_cls: LLMProvider subclass.

        Raises:
            ValueError: If name is empty or provider_cls is invalid.
        """
        clean_name = name.strip().lower()
        if not clean_name:
            raise ValueError("Provider name cannot be empty")
        if not issubclass(provider_cls, LLMProvider):
            raise ValueError(f"{provider_cls} must be a subclass of LLMProvider")
        self._provider_classes[clean_name] = provider_cls

    def register_instance(self, name: str, provider: LLMProvider) -> None:
        """Register a pre-constructed LLMProvider instance by name.

        Args:
            name: Normalized provider name (e.g. 'openai').
            provider: Active LLMProvider instance.

        Raises:
            ValueError: If name is empty or provider is invalid.
        """
        clean_name = name.strip().lower()
        if not clean_name:
            raise ValueError("Provider name cannot be empty")
        if not isinstance(provider, LLMProvider):
            raise ValueError(f"{provider} must be an instance of LLMProvider")
        self._provider_instances[clean_name] = provider

    def get_class(self, name: str) -> type[LLMProvider]:
        """Get registered LLMProvider class by name.

        Args:
            name: Provider name string.

        Returns:
            The registered LLMProvider class.

        Raises:
            ProviderError: If provider name is not registered.
        """
        clean_name = name.strip().lower()
        cls = self._provider_classes.get(clean_name)
        if cls is None:
            raise ProviderError(
                f"LLM provider '{name}' is not registered. "
                f"Available providers: {self.list_providers()}",
                provider=clean_name,
            )
        return cls

    def get_instance(self, name: str) -> LLMProvider | None:
        """Get registered pre-constructed LLMProvider instance, if available.

        Args:
            name: Provider name string.

        Returns:
            Registered LLMProvider instance or None.
        """
        clean_name = name.strip().lower()
        return self._provider_instances.get(clean_name)

    def is_registered(self, name: str) -> bool:
        """Check whether a provider name is registered.

        Args:
            name: Provider name string.

        Returns:
            True if provider class or instance is registered, False otherwise.
        """
        clean_name = name.strip().lower()
        return (
            clean_name in self._provider_classes
            or clean_name in self._provider_instances
        )

    def list_providers(self) -> list[str]:
        """Return list of all registered provider names.

        Returns:
            Sorted list of registered provider names.
        """
        names = set(self._provider_classes.keys()) | set(
            self._provider_instances.keys()
        )
        return sorted(names)

    def clear(self) -> None:
        """Clear all registered classes and instances."""
        self._provider_classes.clear()
        self._provider_instances.clear()


# Default global registry singleton
default_registry = LLMProviderRegistry()


def get_default_registry() -> LLMProviderRegistry:
    """Return the default LLMProviderRegistry singleton.

    Returns:
        The global default LLMProviderRegistry instance.
    """
    return default_registry
