"""Factory for creating providers based on configuration.

This is a stub for Plan 2. Will be used to instantiate providers
based on the selected environment in config.yaml.
"""

from typing import Dict, Any
from nanorec.core.base import Provider
from nanorec.core.registry import get_registry


class ProviderFactory:
    """Creates provider instances based on configuration."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize factory.

        Args:
            config: Full configuration dictionary
        """
        self.config = config
        self.environment = config["environment"]
        self.registry = get_registry()

    def create_provider(self, service: str) -> Provider:
        """
        Create a provider instance for a specific service.

        Args:
            service: Service name (storage, kafka, flink, etc.)

        Returns:
            Provider instance for the configured environment

        Raises:
            NotImplementedError: This is a stub for Plan 2
        """
        raise NotImplementedError(
            "ProviderFactory.create_provider() will be implemented in Plan 2"
        )
