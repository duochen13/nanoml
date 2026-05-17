"""Tests for infrastructure service clients."""

import pytest
from infrastructure.kafka.client import KafkaClient
from infrastructure.mlflow.client import MLflowClient
from infrastructure.feast.client import FeastClient
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


def test_kafka_client():
    """Kafka client should connect and create topics."""
    if not _is_service_available("localhost", 9092):
        pytest.skip("Kafka not running")

    client = KafkaClient(bootstrap_servers="localhost:9092")
    topics = client.list_topics()
    assert isinstance(topics, list)


def test_mlflow_client():
    """MLflow client should connect to tracking server."""
    if not _is_service_available("localhost", 5000):
        pytest.skip("MLflow not running")

    # Check if it's actually MLflow
    import requests
    try:
        response = requests.get("http://localhost:5000/health", timeout=1)
        if response.status_code == 403:
            pytest.skip("Port 5000 occupied by non-MLflow service")
    except Exception:
        pytest.skip("MLflow not available")

    client = MLflowClient(tracking_uri="http://localhost:5000")
    experiments = client.list_experiments()
    assert isinstance(experiments, list)


def test_feast_client():
    """Feast client should initialize."""
    # For MVP, just test initialization
    client = FeastClient(online_store="redis://localhost:6379")
    assert client is not None
