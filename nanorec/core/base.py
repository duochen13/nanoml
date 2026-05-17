"""Base classes for NanoRec components and providers."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class Component(ABC):
    """
    Base class for all NanoRec components.

    Components are user-facing modules (data, features, training, etc.)
    that orchestrate business logic and use infrastructure services.
    """

    def __init__(self, name: str, config: Dict[str, Any] = None):
        """
        Initialize component.

        Args:
            name: Component name
            config: Component-specific configuration
        """
        self.name = name
        self.config = config or {}

    @abstractmethod
    def run(self) -> Any:
        """
        Execute the component's main logic.

        Returns:
            Component execution result
        """
        pass


class Provider(ABC):
    """
    Base class for cloud provider implementations.

    Providers implement infrastructure services for specific
    cloud platforms (local, AWS, GCP, Azure).
    """

    def __init__(self, environment: str, config: Dict[str, Any] = None):
        """
        Initialize provider.

        Args:
            environment: Target environment (local/aws/gcp/azure)
            config: Environment-specific configuration
        """
        self.environment = environment
        self.config = config or {}

    @abstractmethod
    def deploy(self) -> None:
        """Deploy infrastructure services for this provider."""
        pass
