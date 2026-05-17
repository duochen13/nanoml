import subprocess
from pathlib import Path
import pytest
import shutil


def test_docker_compose_config_valid():
    """Docker Compose configuration should be valid."""
    # Skip if docker-compose not available
    if not shutil.which("docker-compose") and not shutil.which("docker"):
        pytest.skip("docker-compose not available")

    result = subprocess.run(
        ["docker-compose", "-f", "deployment/docker-compose.yaml", "config"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Invalid docker-compose.yaml: {result.stderr}"
