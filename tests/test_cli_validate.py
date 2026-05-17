from pathlib import Path
from click.testing import CliRunner
from nanoml.cli.main import cli


def test_validate_valid_config(tmp_path):
    """Validate should pass for valid config."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Create valid config
        config_content = """
environment: local

project:
  name: test-project
  version: 1.0.0

local:
  storage:
    type: localstack

ml:
  features:
    required_features:
      - user:avg_rating
"""
        Path("config.yaml").write_text(config_content)

        result = runner.invoke(cli, ["validate"])

        assert result.exit_code == 0
        assert "✅" in result.output or "valid" in result.output.lower()


def test_validate_invalid_config(tmp_path):
    """Validate should fail for invalid config."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Create invalid config (missing required 'project' field)
        config_content = """
environment: local
"""
        Path("config.yaml").write_text(config_content)

        result = runner.invoke(cli, ["validate"])

        assert result.exit_code != 0
        assert "❌" in result.output or "error" in result.output.lower()


def test_validate_missing_config(tmp_path):
    """Validate should fail if config.yaml doesn't exist."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["validate"])

        assert result.exit_code != 0
        # Click validates path before our code, so either message is acceptable
        assert "not found" in result.output.lower() or "does not exist" in result.output.lower()


def test_validate_custom_path(tmp_path):
    """Validate should accept custom config path."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Create valid config with custom name
        config_content = """
environment: local

project:
  name: test-project
  version: 1.0.0
"""
        Path("custom.yaml").write_text(config_content)

        result = runner.invoke(cli, ["validate", "--config", "custom.yaml"])

        assert result.exit_code == 0
