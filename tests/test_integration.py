"""End-to-end integration tests for NanoML CLI."""

from pathlib import Path
from click.testing import CliRunner
from nanoml.cli.main import cli


def test_end_to_end_workflow(tmp_path):
    """Test complete workflow: init → validate."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Step 1: Initialize project
        result = runner.invoke(cli, ["init", "my-recommender"])
        assert result.exit_code == 0
        assert Path("my-recommender").exists()

        # Step 2: Validate created config
        result = runner.invoke(
            cli,
            ["validate", "--config", "my-recommender/config.yaml"]
        )
        assert result.exit_code == 0
        assert "✅" in result.output

        # Step 3: Verify project structure
        project_dir = Path("my-recommender")

        # User files should exist
        assert (project_dir / "data" / "loader.py").exists()
        assert (project_dir / "features" / "definitions.py").exists()
        assert (project_dir / "training" / "model.py").exists()
        assert (project_dir / "serving" / "recommendation.py").exists()

        # Config should be valid
        assert (project_dir / "config.yaml").exists()
        config_content = (project_dir / "config.yaml").read_text()
        assert "my-recommender" in config_content
        assert "environment: local" in config_content


def test_init_multiple_projects(tmp_path):
    """Should be able to create multiple projects."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Create first project
        result = runner.invoke(cli, ["init", "project-one"])
        assert result.exit_code == 0

        # Create second project
        result = runner.invoke(cli, ["init", "project-two"])
        assert result.exit_code == 0

        # Both should exist
        assert Path("project-one").exists()
        assert Path("project-two").exists()

        # Both configs should be valid
        result = runner.invoke(cli, ["validate", "-c", "project-one/config.yaml"])
        assert result.exit_code == 0

        result = runner.invoke(cli, ["validate", "-c", "project-two/config.yaml"])
        assert result.exit_code == 0
