import pytest
from click.testing import CliRunner
from cli.main import cli
from pathlib import Path


def test_deploy_command_validates_provider(tmp_path, monkeypatch):
    """nanorec deploy validates provider config."""
    # Create invalid config
    config = tmp_path / "nanorec.yaml"
    config.write_text("name: test\nversion: 0.1.0\ninfrastructure:\n  provider: invalid")

    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(cli, ["deploy"])

    assert result.exit_code != 0
    assert "Invalid provider" in result.output


def test_deploy_command_aws_synthesizes_cdk(tmp_path, monkeypatch):
    """nanorec deploy --provider aws synthesizes CDK."""
    config = tmp_path / "nanorec.yaml"
    config.write_text("""
name: test
version: 0.1.0
infrastructure:
  provider: aws
  aws:
    region: us-east-1
    account_id: "123456789012"
""")

    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    # Mock the CDK synth subprocess call
    import subprocess
    original_run = subprocess.run

    def mock_run(cmd, *args, **kwargs):
        if "cdk" in cmd:
            from unittest.mock import Mock
            result = Mock()
            result.returncode = 0
            result.stdout = "CDK synthesized"
            result.stderr = ""
            return result
        return original_run(cmd, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", mock_run)

    result = runner.invoke(cli, ["deploy", "--provider", "aws", "--dry-run"])

    assert result.exit_code == 0
    assert "Synthesizing CDK" in result.output


def test_deploy_command_local_starts_docker_compose(tmp_path, monkeypatch):
    """nanorec deploy --provider local starts Docker Compose."""
    config = tmp_path / "nanorec.yaml"
    config.write_text("""
name: test
version: 0.1.0
infrastructure:
  provider: local
""")

    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    # Mock the docker-compose subprocess call
    import subprocess
    original_run = subprocess.run

    def mock_run(cmd, *args, **kwargs):
        if "docker-compose" in cmd:
            from unittest.mock import Mock
            result = Mock()
            result.returncode = 0
            result.stdout = "Docker Compose started"
            result.stderr = ""
            return result
        return original_run(cmd, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", mock_run)

    result = runner.invoke(cli, ["deploy", "--provider", "local"])

    assert result.exit_code == 0
    assert "Starting local infrastructure" in result.output
