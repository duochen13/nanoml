"""Docker Compose file parser and container auto-discovery."""

import yaml
import docker
from typing import Dict, List, Any, Optional
from pathlib import Path


class DockerComposeParser:
    """Parse docker-compose.yaml and match with running containers."""

    def __init__(self, compose_file_path: str):
        """Initialize parser with compose file path.

        Args:
            compose_file_path: Path to docker-compose.yaml file
        """
        self.compose_file_path = Path(compose_file_path)
        self.docker_client = docker.from_env()

    def parse_compose_file(self) -> Dict[str, Any]:
        """Parse docker-compose.yaml file.

        Returns:
            Dictionary with parsed compose file content
        """
        if not self.compose_file_path.exists():
            raise FileNotFoundError(f"Compose file not found: {self.compose_file_path}")

        with open(self.compose_file_path, 'r') as f:
            return yaml.safe_load(f)

    def get_service_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Extract service definitions from compose file.

        Returns:
            Dictionary mapping service names to their configurations
        """
        compose_data = self.parse_compose_file()
        return compose_data.get('services', {})

    def get_running_containers(self) -> List[docker.models.containers.Container]:
        """Get all running Docker containers.

        Returns:
            List of running container objects
        """
        return self.docker_client.containers.list()

    def match_service_to_container(
        self,
        service_name: str,
        service_config: Dict[str, Any]
    ) -> Optional[docker.models.containers.Container]:
        """Match a docker-compose service to a running container.

        Args:
            service_name: Name of the service from docker-compose
            service_config: Service configuration from docker-compose

        Returns:
            Container object if found, None otherwise
        """
        containers = self.get_running_containers()

        # Try multiple matching strategies
        for container in containers:
            # Strategy 1: Match by compose labels
            labels = container.labels
            compose_service = labels.get('com.docker.compose.service')
            compose_project = labels.get('com.docker.compose.project')

            if compose_service == service_name:
                return container

            # Strategy 2: Match by container name containing service name
            if service_name in container.name:
                return container

        return None

    def discover_all_services(self) -> List[Dict[str, Any]]:
        """Discover all services from docker-compose and match to running containers.

        Returns:
            List of dictionaries with service info and matching container details
        """
        services = self.get_service_definitions()
        discovered = []

        for service_name, service_config in services.items():
            container = self.match_service_to_container(service_name, service_config)

            if container:
                # Extract image from service config or container
                image = service_config.get('image', container.image.tags[0] if container.image.tags else 'unknown')

                discovered.append({
                    'service_name': service_name,
                    'container_id': container.id,
                    'container_name': container.name,
                    'image': image,
                    'status': container.status,
                    'ports': service_config.get('ports', []),
                    'environment': service_config.get('environment', {}),
                    'compose_config': service_config
                })
            else:
                # Service defined but not running
                discovered.append({
                    'service_name': service_name,
                    'container_id': None,
                    'container_name': None,
                    'image': service_config.get('image', 'unknown'),
                    'status': 'not_running',
                    'ports': service_config.get('ports', []),
                    'environment': service_config.get('environment', {}),
                    'compose_config': service_config
                })

        return discovered

    def get_registerable_containers(self) -> List[Dict[str, str]]:
        """Get list of running containers that can be registered for monitoring.

        Returns:
            List of dictionaries with container_id, container_name, and image
        """
        discovered = self.discover_all_services()

        registerable = []
        for service in discovered:
            if service['status'] != 'not_running' and service['container_id']:
                registerable.append({
                    'service_name': service['service_name'],
                    'container_id': service['container_id'],
                    'container_name': service['container_name'],
                    'image': service['image']
                })

        return registerable
