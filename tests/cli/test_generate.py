import pytest
from pathlib import Path
from click.testing import CliRunner
from cli.main import cli


@pytest.fixture
def sample_project(tmp_path):
    """Create a sample NanoRec project."""
    # Create project structure
    (tmp_path / "nanorec.yaml").write_text("name: test_project\nversion: 0.1.0")
    (tmp_path / "features").mkdir()
    (tmp_path / "components").mkdir()

    # Create sample features
    (tmp_path / "features" / "definitions.py").write_text('''
from nanorec.features import Feature, FeatureGroup

user_features = FeatureGroup(
    name="user_features",
    entity="user_id",
    features=[Feature("age", "int")],
    source="kafka://users"
)
''')

    return tmp_path


def test_generate_creates_all_artifacts(sample_project):
    """nanorec generate creates Flink, Feast, and Airflow code."""
    import os
    runner = CliRunner()

    # Change to sample project directory
    old_cwd = os.getcwd()
    os.chdir(sample_project)

    try:
        result = runner.invoke(cli, ["generate"], catch_exceptions=False)

        assert result.exit_code == 0
        assert "Generated" in result.output or "Generating" in result.output

        # Check files created
        generated_dir = sample_project / ".nanorec" / "generated"
        assert (generated_dir / "flink" / "streaming_features.py").exists()
        assert (generated_dir / "feast" / "feature_store.yaml").exists()
        assert (generated_dir / "feast" / "features.py").exists()
    finally:
        os.chdir(old_cwd)


def test_generate_clean_flag(sample_project):
    """nanorec generate --clean removes existing generated code first."""
    import os
    # Create some existing generated files
    gen_dir = sample_project / ".nanorec" / "generated"
    gen_dir.mkdir(parents=True, exist_ok=True)
    (gen_dir / "old_file.py").write_text("# old")

    runner = CliRunner()

    # Change to sample project directory
    old_cwd = os.getcwd()
    os.chdir(sample_project)

    try:
        result = runner.invoke(cli, ["generate", "--clean"], catch_exceptions=False)

        assert result.exit_code == 0
        assert not (gen_dir / "old_file.py").exists()
    finally:
        os.chdir(old_cwd)


def test_generate_fails_without_nanorec_yaml(tmp_path):
    """nanorec generate fails if not in NanoRec project."""
    import os
    runner = CliRunner()

    # Change to temp directory with no nanorec.yaml
    old_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        result = runner.invoke(cli, ["generate"])

        assert result.exit_code != 0
        assert "No nanorec.yaml found" in result.output
    finally:
        os.chdir(old_cwd)
