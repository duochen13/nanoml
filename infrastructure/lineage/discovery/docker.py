"""Docker container discovery service."""

import docker
from typing import List, Optional
from .base import BaseDiscovery, DiscoveredComponent, ComponentCategory


class DockerDiscovery(BaseDiscovery):
    """Discover ML components running in Docker containers."""

    # Component type mapping based on Docker image names
    IMAGE_TYPE_MAP = {
        "spark": ("spark_cluster", ComponentCategory.PROCESSING),
        "flink": ("flink_cluster", ComponentCategory.STREAMING),
        "kafka": ("kafka_broker", ComponentCategory.STREAMING),
        "mlflow": ("mlflow_server", ComponentCategory.ML),
        "feast": ("feast_server", ComponentCategory.STORAGE),
        "minio": ("s3_compatible", ComponentCategory.DATA_SOURCES),
        "postgres": ("database", ComponentCategory.STORAGE),
        "mysql": ("database", ComponentCategory.STORAGE),
        "redis": ("cache", ComponentCategory.STORAGE),
        "jupyter": ("notebook", ComponentCategory.ML),
        "tensorflow": ("ml_runtime", ComponentCategory.ML),
        "pytorch": ("ml_runtime", ComponentCategory.ML),
        "ray": ("ml_platform", ComponentCategory.ML),
    }

    def __init__(self):
        """Initialize Docker discovery."""
        self._client: Optional[docker.DockerClient] = None

    def is_available(self) -> bool:
        """Check if Docker is available."""
        try:
            client = docker.from_env()
            client.ping()
            return True
        except Exception:
            return False

    async def discover(self) -> List[DiscoveredComponent]:
        """Discover running Docker containers.

        Returns:
            List of discovered components from Docker
        """
        if not self.is_available():
            return []

        components = []

        try:
            client = docker.from_env()
            containers = client.containers.list(all=False)  # Only running containers

            for container in containers:
                component = self._parse_container(container)
                if component:
                    components.append(component)

        except Exception as e:
            print(f"Error discovering Docker containers: {e}")

        return components

    def _parse_container(self, container) -> Optional[DiscoveredComponent]:
        """Parse a Docker container into a component.

        Args:
            container: Docker container object

        Returns:
            DiscoveredComponent if recognized, None otherwise
        """
        try:
            image_name = container.image.tags[0] if container.image.tags else ""
            image_name_lower = image_name.lower()

            # Detect component type from image name
            component_type = "unknown"
            category = ComponentCategory.PROCESSING

            for key, (ctype, cat) in self.IMAGE_TYPE_MAP.items():
                if key in image_name_lower:
                    component_type = ctype
                    category = cat
                    break

            # Skip generic containers we don't care about
            if component_type == "unknown":
                return None

            # Extract ports
            ports = []
            if container.ports:
                for port_key, port_bindings in container.ports.items():
                    if port_bindings:
                        for binding in port_bindings:
                            ports.append(f"{binding['HostIp']}:{binding['HostPort']}")

            # Build component
            component = DiscoveredComponent(
                id=f"docker_{container.short_id}",
                name=container.name,
                type=component_type,
                provider="docker",
                category=category,
                metadata={
                    "container_id": container.short_id,
                    "image": image_name,
                    "status": container.status,
                    "ports": ports,
                    "labels": container.labels,
                    "created": container.attrs.get("Created", ""),
                }
            )

            return component

        except Exception as e:
            print(f"Error parsing container {container.short_id}: {e}")
            return None
