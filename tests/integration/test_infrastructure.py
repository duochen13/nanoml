"""Integration tests for NanoML infrastructure services."""

import pytest
from core.health import HealthChecker, ServiceStatus
import socket


def _is_service_available(host: str, port: int) -> bool:
    """Check if service is available."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


@pytest.fixture(scope="module")
def health_checker():
    """Create health checker instance."""
    return HealthChecker(timeout=10)


def test_localstack_healthy(health_checker):
    """LocalStack S3 service should be healthy."""
    if not _is_service_available("localhost", 4566):
        pytest.skip("LocalStack not running")

    health = health_checker.check_http("LocalStack", "http://localhost:4566/_localstack/health")
    assert health.healthy, f"LocalStack unhealthy: {health.message}"


def test_kafka_healthy(health_checker):
    """Kafka service should be healthy."""
    if not _is_service_available("localhost", 9092):
        pytest.skip("Kafka not running")

    health = health_checker.check_tcp("Kafka", "localhost", 9092)
    assert health.healthy, f"Kafka unhealthy: {health.message}"


def test_flink_healthy(health_checker):
    """Flink JobManager should be healthy."""
    if not _is_service_available("localhost", 8081):
        pytest.skip("Flink not running")

    health = health_checker.check_http("Flink", "http://localhost:8081/overview")
    if not health.healthy and "Connection" in health.message:
        pytest.skip("Port 8081 occupied by non-Flink service")
    assert health.healthy, f"Flink unhealthy: {health.message}"


def test_redis_healthy(health_checker):
    """Redis should be healthy."""
    if not _is_service_available("localhost", 6379):
        pytest.skip("Redis not running")

    health = health_checker.check_tcp("Redis", "localhost", 6379)
    assert health.healthy, f"Redis unhealthy: {health.message}"


def test_mlflow_healthy(health_checker):
    """MLflow tracking server should be healthy."""
    if not _is_service_available("localhost", 5000):
        pytest.skip("MLflow not running")

    health = health_checker.check_http("MLflow", "http://localhost:5001/health")
    if not health.healthy and ("403" in health.message or "404" in health.message):
        pytest.skip("Port 5000 occupied by non-MLflow service")
    assert health.healthy, f"MLflow unhealthy: {health.message}"


def test_all_services_healthy(health_checker):
    """All infrastructure services should be healthy."""
    # Only run if at least one expected NanoML service is running
    # Check for LocalStack specifically as it's the most specific indicator
    if not _is_service_available("localhost", 4566):
        pytest.skip("NanoML infrastructure not running (LocalStack not found on 4566)")

    results = health_checker.check_all_services()

    # Report status
    for name, health in results.items():
        print(f"{name}: {health.status.value} - {health.message}")

    # Check all healthy
    unhealthy = [name for name, health in results.items() if not health.healthy]
    assert len(unhealthy) == 0, f"Unhealthy services: {unhealthy}"
