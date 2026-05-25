"""Base abstraction for monitored components."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class HealthStatus(str, Enum):
    """Component health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Health check result."""
    status: HealthStatus
    message: str
    checked_at: datetime
    details: Dict[str, Any]


@dataclass
class Metric:
    """Component metric."""
    name: str
    value: Any
    unit: Optional[str]
    timestamp: datetime
    labels: Dict[str, str]


class AbstractComponent(ABC):
    """Base class for all component adapters.

    Provides standardized interface for:
    - Health checks
    - Metrics collection
    - Metadata retrieval
    - Lineage tracking
    """

    def __init__(self, component_id: str, component_name: str, component_type: str):
        """Initialize component adapter.

        Args:
            component_id: Unique component identifier
            component_name: Human-readable name
            component_type: Component type (e.g., "s3_bucket", "spark_cluster")
        """
        self.component_id = component_id
        self.component_name = component_name
        self.component_type = component_type

    @abstractmethod
    async def health_check(self) -> HealthCheck:
        """Check component health.

        Returns:
            HealthCheck with status and details
        """
        pass

    @abstractmethod
    async def get_metrics(self) -> List[Metric]:
        """Collect component metrics.

        Returns:
            List of metrics (size, throughput, latency, etc.)
        """
        pass

    @abstractmethod
    async def get_metadata(self) -> Dict[str, Any]:
        """Get component metadata.

        Returns:
            Dictionary with component-specific metadata
        """
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.component_id,
            "name": self.component_name,
            "type": self.component_type,
        }


class DataSourceAdapter(AbstractComponent):
    """Abstract adapter for data sources (S3, GCS, databases)."""

    @abstractmethod
    async def get_schema(self) -> Optional[Dict[str, Any]]:
        """Get data schema.

        Returns:
            Schema definition or None if not applicable
        """
        pass

    @abstractmethod
    async def get_size_bytes(self) -> int:
        """Get data size in bytes.

        Returns:
            Size in bytes
        """
        pass


class ProcessingAdapter(AbstractComponent):
    """Abstract adapter for processing engines (Spark, Flink)."""

    @abstractmethod
    async def get_job_status(self) -> Dict[str, Any]:
        """Get current job status.

        Returns:
            Job status information
        """
        pass

    @abstractmethod
    async def get_logs(self, limit: int = 100) -> List[str]:
        """Get recent logs.

        Args:
            limit: Maximum number of log lines

        Returns:
            List of log lines
        """
        pass


class MLAdapter(AbstractComponent):
    """Abstract adapter for ML components (MLflow, model servers)."""

    @abstractmethod
    async def get_model_info(self) -> Dict[str, Any]:
        """Get model information.

        Returns:
            Model metadata (version, accuracy, etc.)
        """
        pass

    @abstractmethod
    async def get_predictions_count(self) -> int:
        """Get total prediction count.

        Returns:
            Number of predictions served
        """
        pass
