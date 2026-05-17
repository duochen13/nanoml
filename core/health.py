"""Health check utilities for NanoML infrastructure services."""

import requests
import socket
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class ServiceStatus(Enum):
    """Service health status."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceHealth:
    """Health status for a service."""
    name: str
    healthy: bool
    message: str
    status: ServiceStatus = ServiceStatus.UNKNOWN

    def __post_init__(self):
        self.status = ServiceStatus.HEALTHY if self.healthy else ServiceStatus.UNHEALTHY


class HealthChecker:
    """Check health of NanoML infrastructure services."""

    def __init__(self, timeout: int = 5):
        """
        Initialize health checker.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout

    def check_http(self, name: str, url: str, expected_status: int = 200) -> ServiceHealth:
        """
        Check HTTP service health.

        Args:
            name: Service name
            url: Health check URL
            expected_status: Expected HTTP status code

        Returns:
            ServiceHealth object
        """
        try:
            response = requests.get(url, timeout=self.timeout)
            healthy = response.status_code == expected_status
            message = f"HTTP {response.status_code}" if healthy else f"Expected {expected_status}, got {response.status_code}"
            return ServiceHealth(name=name, healthy=healthy, message=message)
        except requests.RequestException as e:
            return ServiceHealth(name=name, healthy=False, message=f"Connection failed: {e}")

    def check_tcp(self, name: str, host: str, port: int) -> ServiceHealth:
        """
        Check TCP service health.

        Args:
            name: Service name
            host: Service host
            port: Service port

        Returns:
            ServiceHealth object
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            healthy = result == 0
            message = "Port open" if healthy else f"Port closed (code: {result})"
            return ServiceHealth(name=name, healthy=healthy, message=message)
        except Exception as e:
            return ServiceHealth(name=name, healthy=False, message=f"Check failed: {e}")

    def check_all_services(self) -> Dict[str, ServiceHealth]:
        """
        Check health of all NanoML services.

        Returns:
            Dictionary mapping service name to health status
        """
        services = {
            "localstack": self.check_http("LocalStack", "http://localhost:4566/_localstack/health"),
            "kafka": self.check_tcp("Kafka", "localhost", 9092),
            "flink": self.check_http("Flink", "http://localhost:8081/overview"),
            "redis": self.check_tcp("Redis", "localhost", 6379),
            "mlflow": self.check_http("MLflow", "http://localhost:5000/health"),
            "api": self.check_http("API Gateway", "http://localhost:8000/health"),
            "airflow": self.check_http("Airflow", "http://localhost:8080/health"),
            "lineage": self.check_http("Lineage API", "http://localhost:9000/health"),
            "dashboard": self.check_http("Dashboard", "http://localhost:3000"),
        }
        return services

    def wait_for_services(self, max_attempts: int = 30, delay: int = 2) -> bool:
        """
        Wait for all services to become healthy.

        Args:
            max_attempts: Maximum number of attempts
            delay: Delay between attempts in seconds

        Returns:
            True if all services healthy, False otherwise
        """
        import time

        for attempt in range(max_attempts):
            results = self.check_all_services()
            all_healthy = all(health.healthy for health in results.values())

            if all_healthy:
                return True

            unhealthy = [name for name, health in results.items() if not health.healthy]
            print(f"Attempt {attempt + 1}/{max_attempts}: Waiting for {unhealthy}")
            time.sleep(delay)

        return False
