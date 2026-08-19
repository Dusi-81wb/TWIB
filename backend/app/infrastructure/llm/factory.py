"""LLM Provider Factory.

Responsible for instantiating and resolving LLMProvider instances using the
LLMProviderRegistry and application settings. Services request provider
instances through this factory rather than instantiating provider classes
directly.
"""

from __future__ import annotations

from app.core.config import get_settings
from app.core.settings import ApplicationSettings
from app.infrastructure.llm.exceptions import ProviderError
from app.infrastructure.llm.provider import LLMProvider
from app.infrastructure.llm.providers.ollama_provider import OllamaProvider
from app.infrastructure.llm.providers.openai_provider import OpenAIProvider
from app.infrastructure.llm.registry import (
    LLMProviderRegistry,
    get_default_registry,
)


class LLMProviderFactory:
    """Factory creating and resolving LLMProvider instances.

    Attributes:
        _registry: LLMProviderRegistry instance used for lookup.
        _settings: ApplicationSettings instance.
        _instances: Cache of instantiated provider objects.
    """

    def __init__(
        self,
        registry: LLMProviderRegistry | None = None,
        settings: ApplicationSettings | None = None,
    ) -> None:
        """Initialize LLMProviderFactory.

        Args:
            registry: Optional custom registry instance (defaults to global default).
            settings: Optional ApplicationSettings instance (defaults to settings).
        """
        self._registry = registry or get_default_registry()
        self._settings = settings or get_settings()
        self._instances: dict[str, LLMProvider] = {}
        self._register_default_providers()

    def get_provider(self, name: str) -> LLMProvider:
        """Resolve and return an LLMProvider instance by name.

        Args:
            name: Provider identifier (e.g. 'openai', 'ollama').

        Returns:
            Instantiated LLMProvider object.

        Raises:
            ProviderError: If provider is unknown or fails to instantiate.
        """
        clean_name = name.strip().lower()

        # 1. Check factory local instance cache
        if clean_name in self._instances:
            return self._instances[clean_name]

        # 2. Check registry pre-constructed instances
        instance = self._registry.get_instance(clean_name)
        if instance is not None:
            self._instances[clean_name] = instance
            return instance

        # 3. Resolve class from registry and instantiate
        provider_cls = self._registry.get_class(clean_name)
        try:
            new_instance = provider_cls(settings=self._settings)
            self._instances[clean_name] = new_instance
            return new_instance
        except Exception as err:
            raise ProviderError(
                f"Failed to instantiate LLM provider '{name}': {err}",
                provider=clean_name,
            ) from err

    def register_provider(self, name: str, provider_cls: type[LLMProvider]) -> None:
        """Register a new LLMProvider class in the underlying registry.

        Args:
            name: Provider name identifier string.
            provider_cls: Subclass of LLMProvider.
        """
        self._registry.register_class(name, provider_cls)

    def is_registered(self, name: str) -> bool:
        """Check whether a provider name is registered.

        Args:
            name: Provider name string.

        Returns:
            True if registered, False otherwise.
        """
        return self._registry.is_registered(name)

    def list_providers(self) -> list[str]:
        """List all available provider names.

        Returns:
            Sorted list of provider names.
        """
        return self._registry.list_providers()

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    def _register_default_providers(self) -> None:
        """Ensure standard built-in providers are registered."""
        if not self._registry.is_registered("omniroute"):
            self._registry.register_class("omniroute", OpenAIProvider)
        if not self._registry.is_registered("openai"):
            self._registry.register_class("openai", OpenAIProvider)
        if not self._registry.is_registered("ollama"):
            self._registry.register_class("ollama", OllamaProvider)
