"""Component and provider registry.

This is a stub for Plan 2. Will be used to register and discover
components and providers at runtime.
"""

from typing import Dict, Type
from nanorec.core.base import Component, Provider


class Registry:
    """Registry for components and providers."""

    def __init__(self):
        self._components: Dict[str, Type[Component]] = {}
        self._providers: Dict[str, Type[Provider]] = {}

    def register_component(self, name: str, component_class: Type[Component]) -> None:
        """
        Register a component class.

        Args:
            name: Component name
            component_class: Component class
        """
        self._components[name] = component_class

    def register_provider(self, name: str, provider_class: Type[Provider]) -> None:
        """
        Register a provider class.

        Args:
            name: Provider name
            provider_class: Provider class
        """
        self._providers[name] = provider_class

    def get_component(self, name: str) -> Type[Component]:
        """Get registered component class."""
        if name not in self._components:
            raise KeyError(f"Component not registered: {name}")
        return self._components[name]

    def get_provider(self, name: str) -> Type[Provider]:
        """Get registered provider class."""
        if name not in self._providers:
            raise KeyError(f"Provider not registered: {name}")
        return self._providers[name]


# Global registry instance
_registry = Registry()


def get_registry() -> Registry:
    """Get the global registry instance."""
    return _registry
