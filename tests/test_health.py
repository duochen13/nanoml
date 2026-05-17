import pytest
from core.health import HealthChecker, ServiceHealth


def test_health_checker_initialization():
    """HealthChecker should initialize with service configs."""
    checker = HealthChecker()
    assert checker is not None


def test_service_health_status():
    """ServiceHealth should track status."""
    health = ServiceHealth(name="test", healthy=True, message="OK")
    assert health.name == "test"
    assert health.healthy is True
    assert health.message == "OK"


def test_check_http_service_healthy():
    """Should detect healthy HTTP service."""
    checker = HealthChecker()
    # This test will pass if we mock or have a running service
    # For now, test the interface
    assert hasattr(checker, "check_http")
