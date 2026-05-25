"""Monitoring service for all components."""

from typing import Dict, Any, List
from datetime import datetime
from .base import AbstractComponent, HealthStatus
from .s3 import S3Adapter
from .mlflow import MLflowAdapter
from .docker_component import DockerContainerAdapter


class ComponentMonitor:
    """Monitors health and metrics for all discovered components."""

    def __init__(self):
        """Initialize component monitor."""
        self.components: Dict[str, AbstractComponent] = {}

    def register_s3_bucket(self, bucket_name: str, region: str = "us-east-1", prefix: str = ""):
        """Register S3 bucket for monitoring.

        Args:
            bucket_name: S3 bucket name
            region: AWS region
            prefix: Optional prefix
        """
        adapter = S3Adapter(bucket_name, region, prefix)
        self.components[adapter.component_id] = adapter

    def register_mlflow_server(self, tracking_uri: str, model_name: str = None):
        """Register MLflow server for monitoring.

        Args:
            tracking_uri: MLflow tracking URI
            model_name: Optional model name
        """
        adapter = MLflowAdapter(tracking_uri, model_name)
        self.components[adapter.component_id] = adapter

    def register_docker_container(self, container_id: str, container_name: str, image: str):
        """Register Docker container for monitoring.

        Args:
            container_id: Container ID
            container_name: Container name
            image: Docker image
        """
        adapter = DockerContainerAdapter(container_id, container_name, image)
        self.components[adapter.component_id] = adapter

    async def health_check_all(self) -> Dict[str, Any]:
        """Run health checks on all registered components.

        Returns:
            Dictionary with health status for each component
        """
        results = {}

        for component_id, component in self.components.items():
            try:
                health = await component.health_check()
                results[component_id] = {
                    "name": component.component_name,
                    "type": component.component_type,
                    "status": health.status.value,
                    "message": health.message,
                    "checked_at": health.checked_at.isoformat(),
                    "details": health.details
                }
            except Exception as e:
                results[component_id] = {
                    "name": component.component_name,
                    "type": component.component_type,
                    "status": HealthStatus.UNKNOWN.value,
                    "message": f"Error: {str(e)}",
                    "checked_at": datetime.utcnow().isoformat(),
                    "details": {}
                }

        # Calculate overall health
        statuses = [r["status"] for r in results.values()]
        overall = "healthy"
        if any(s == "unhealthy" for s in statuses):
            overall = "unhealthy"
        elif any(s == "degraded" for s in statuses):
            overall = "degraded"

        return {
            "overall_status": overall,
            "components": results,
            "summary": {
                "total": len(results),
                "healthy": sum(1 for s in statuses if s == "healthy"),
                "degraded": sum(1 for s in statuses if s == "degraded"),
                "unhealthy": sum(1 for s in statuses if s == "unhealthy"),
                "unknown": sum(1 for s in statuses if s == "unknown"),
            }
        }

    async def collect_metrics_all(self) -> Dict[str, Any]:
        """Collect metrics from all registered components.

        Returns:
            Dictionary with metrics for each component
        """
        results = {}

        for component_id, component in self.components.items():
            try:
                metrics = await component.get_metrics()
                results[component_id] = {
                    "name": component.component_name,
                    "type": component.component_type,
                    "metrics": [
                        {
                            "name": m.name,
                            "value": m.value,
                            "unit": m.unit,
                            "timestamp": m.timestamp.isoformat(),
                            "labels": m.labels
                        }
                        for m in metrics
                    ]
                }
            except Exception as e:
                results[component_id] = {
                    "name": component.component_name,
                    "type": component.component_type,
                    "error": str(e)
                }

        return {
            "components": results,
            "collected_at": datetime.utcnow().isoformat()
        }

    async def get_component_detail(self, component_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific component.

        Args:
            component_id: Component ID

        Returns:
            Dictionary with health, metrics, and metadata
        """
        if component_id not in self.components:
            return {"error": "Component not found"}

        component = self.components[component_id]

        try:
            health = await component.health_check()
            metrics = await component.get_metrics()
            metadata = await component.get_metadata()

            return {
                "id": component_id,
                "name": component.component_name,
                "type": component.component_type,
                "health": {
                    "status": health.status.value,
                    "message": health.message,
                    "checked_at": health.checked_at.isoformat(),
                    "details": health.details
                },
                "metrics": [
                    {
                        "name": m.name,
                        "value": m.value,
                        "unit": m.unit,
                        "timestamp": m.timestamp.isoformat(),
                        "labels": m.labels
                    }
                    for m in metrics
                ],
                "metadata": metadata
            }

        except Exception as e:
            return {
                "id": component_id,
                "name": component.component_name,
                "type": component.component_type,
                "error": str(e)
            }

    def list_components(self) -> List[Dict[str, str]]:
        """List all registered components.

        Returns:
            List of component summaries
        """
        return [
            {
                "id": component_id,
                "name": component.component_name,
                "type": component.component_type
            }
            for component_id, component in self.components.items()
        ]
