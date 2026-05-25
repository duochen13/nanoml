"""Docker container adapter with monitoring."""

from typing import Dict, Any, List
from datetime import datetime
from .base import ProcessingAdapter, HealthCheck, HealthStatus, Metric

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False


class DockerContainerAdapter(ProcessingAdapter):
    """Adapter for Docker containers running ML components."""

    def __init__(self, container_id: str, container_name: str, image: str):
        """Initialize Docker container adapter.

        Args:
            container_id: Docker container ID
            container_name: Container name
            image: Docker image name
        """
        super().__init__(
            component_id=f"docker_{container_id}",
            component_name=container_name,
            component_type="docker_container"
        )
        self.container_id = container_id
        self.image = image
        self._client = None
        self._container = None

    def _get_container(self):
        """Get container object."""
        if self._container is None and DOCKER_AVAILABLE:
            self._client = docker.from_env()
            self._container = self._client.containers.get(self.container_id)
        return self._container

    async def health_check(self) -> HealthCheck:
        """Check container health."""
        if not DOCKER_AVAILABLE:
            return HealthCheck(
                status=HealthStatus.UNKNOWN,
                message="docker not available",
                checked_at=datetime.utcnow(),
                details={}
            )

        try:
            container = self._get_container()
            container.reload()

            status = container.status

            if status == "running":
                health_status = HealthStatus.HEALTHY
                message = "Container running"
            elif status in ["created", "restarting"]:
                health_status = HealthStatus.DEGRADED
                message = f"Container {status}"
            else:
                health_status = HealthStatus.UNHEALTHY
                message = f"Container {status}"

            return HealthCheck(
                status=health_status,
                message=message,
                checked_at=datetime.utcnow(),
                details={
                    "container_id": self.container_id,
                    "status": status,
                    "image": self.image
                }
            )

        except Exception as e:
            return HealthCheck(
                status=HealthStatus.UNHEALTHY,
                message=f"Container error: {str(e)}",
                checked_at=datetime.utcnow(),
                details={"error": str(e)}
            )

    async def get_metrics(self) -> List[Metric]:
        """Collect container metrics."""
        metrics = []
        timestamp = datetime.utcnow()

        try:
            container = self._get_container()

            # Get stats
            stats = container.stats(stream=False)

            # CPU usage
            cpu_stats = stats.get("cpu_stats", {})
            precpu_stats = stats.get("precpu_stats", {})

            cpu_delta = cpu_stats.get("cpu_usage", {}).get("total_usage", 0) - \
                       precpu_stats.get("cpu_usage", {}).get("total_usage", 0)
            system_delta = cpu_stats.get("system_cpu_usage", 0) - \
                          precpu_stats.get("system_cpu_usage", 0)

            if system_delta > 0:
                cpu_percent = (cpu_delta / system_delta) * 100.0
                metrics.append(Metric(
                    name="cpu_usage_percent",
                    value=cpu_percent,
                    unit="percent",
                    timestamp=timestamp,
                    labels={"container": self.component_name}
                ))

            # Memory usage
            mem_stats = stats.get("memory_stats", {})
            mem_usage = mem_stats.get("usage", 0)
            mem_limit = mem_stats.get("limit", 1)
            mem_percent = (mem_usage / mem_limit) * 100.0

            metrics.append(Metric(
                name="memory_usage_bytes",
                value=mem_usage,
                unit="bytes",
                timestamp=timestamp,
                labels={"container": self.component_name}
            ))

            metrics.append(Metric(
                name="memory_usage_percent",
                value=mem_percent,
                unit="percent",
                timestamp=timestamp,
                labels={"container": self.component_name}
            ))

        except Exception as e:
            print(f"Error collecting Docker metrics: {e}")

        return metrics

    async def get_metadata(self) -> Dict[str, Any]:
        """Get container metadata."""
        metadata = {
            "container_id": self.container_id,
            "container_name": self.component_name,
            "image": self.image,
        }

        try:
            container = self._get_container()
            attrs = container.attrs

            metadata["status"] = container.status
            metadata["created"] = attrs.get("Created")
            metadata["ports"] = attrs.get("NetworkSettings", {}).get("Ports", {})
            metadata["labels"] = attrs.get("Config", {}).get("Labels", {})

        except Exception as e:
            metadata["error"] = str(e)

        return metadata

    async def get_job_status(self) -> Dict[str, Any]:
        """Get container status."""
        try:
            container = self._get_container()
            container.reload()

            return {
                "status": container.status,
                "running": container.status == "running"
            }

        except Exception as e:
            return {"error": str(e)}

    async def get_logs(self, limit: int = 100) -> List[str]:
        """Get container logs."""
        try:
            container = self._get_container()
            logs = container.logs(tail=limit, timestamps=True)

            # Decode and split into lines
            log_lines = logs.decode('utf-8').strip().split('\n')

            return log_lines

        except Exception as e:
            return [f"Error getting logs: {str(e)}"]
