import pytest
from pathlib import Path
from click.testing import CliRunner
from nanoml.cli.main import cli


def test_init_creates_project(tmp_path):
    """Init command should create project structure."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["init", "test-project"])

        assert result.exit_code == 0
        assert "Creating NanoML project: test-project" in result.output
        assert "✅ Project created!" in result.output

        # Verify project directory exists
        project_dir = Path("test-project")
        assert project_dir.exists()
        assert project_dir.is_dir()

        # Verify key files exist
        assert (project_dir / "config.yaml").exists()
        assert (project_dir / "README.md").exists()
        assert (project_dir / "Makefile").exists()
        assert (project_dir / "requirements.txt").exists()
        assert (project_dir / ".gitignore").exists()

        # Verify component directories exist
        assert (project_dir / "data").is_dir()
        assert (project_dir / "features").is_dir()
        assert (project_dir / "training").is_dir()
        assert (project_dir / "serving").is_dir()
        assert (project_dir / "infrastructure").is_dir()

        # Verify component files exist
        assert (project_dir / "data" / "loader.py").exists()
        assert (project_dir / "features" / "definitions.py").exists()


def test_init_invalid_name():
    """Init should reject invalid project names."""
    runner = CliRunner()

    # Uppercase not allowed
    result = runner.invoke(cli, ["init", "TestProject"])
    assert result.exit_code != 0
    assert "invalid" in result.output.lower() or "name" in result.output.lower()

    # Spaces not allowed
    result = runner.invoke(cli, ["init", "test project"])
    assert result.exit_code != 0


def test_init_existing_directory(tmp_path):
    """Init should fail if directory already exists."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Create directory
        Path("existing-project").mkdir()

        # Try to init
        result = runner.invoke(cli, ["init", "existing-project"])
        assert result.exit_code != 0
        assert "already exists" in result.output


def test_init_with_template(tmp_path):
    """Init should support --template flag."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["init", "test-project", "--template", "default"])
        assert result.exit_code == 0
        assert Path("test-project").exists()
