"""Base discovery interface for infrastructure components."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ComponentCategory(str, Enum):
    """Component categories matching the workflow node types."""
    DATA_SOURCES = "data_sources"
    PROCESSING = "processing"
    STREAMING = "streaming"
    STORAGE = "storage"
    ML = "ml"
    SERVING = "serving"


@dataclass
class DiscoveredComponent:
    """A discovered infrastructure component."""
    id: str
    name: str
    type: str  # e.g., "s3_bucket", "spark_job", "mlflow_server"
    provider: str  # e.g., "aws", "gcp", "docker", "local"
    category: ComponentCategory
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "provider": self.provider,
            "category": self.category.value,
            "metadata": self.metadata
        }


class BaseDiscovery(ABC):
    """Abstract base class for discovery services."""

    @abstractmethod
    async def discover(self) -> List[DiscoveredComponent]:
        """Discover components from this source.

        Returns:
            List of discovered components
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this discovery source is available/configured.

        Returns:
            True if discovery can be performed
        """
        pass
