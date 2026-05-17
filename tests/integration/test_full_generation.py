import pytest
from pathlib import Path
from click.testing import CliRunner
from cli.main import cli


@pytest.fixture
def full_project(tmp_path):
    """Create a complete NanoML project for testing."""
    # nanoml.yaml
    (tmp_path / "nanoml.yaml").write_text("""
name: movie_recommendations
version: 0.1.0
description: Movie recommendation system
""")

    # features/definitions.py
    features_dir = tmp_path / "features"
    features_dir.mkdir()
    (features_dir / "definitions.py").write_text('''
from nanoml.features import Feature, FeatureGroup

user_features = FeatureGroup(
    name="user_features",
    entity="user_id",
    features=[
        Feature("age", "int"),
        Feature("country", "string"),
        Feature("total_watches", "int")
    ],
    source="kafka://user_events"
)

movie_features = FeatureGroup(
    name="movie_features",
    entity="movie_id",
    features=[
        Feature("genre", "string"),
        Feature("release_year", "int"),
        Feature("avg_rating", "float")
    ],
    source="kafka://movie_events"
)
''')

    # components/pipeline.py
    components_dir = tmp_path / "components"
    components_dir.mkdir()
    (components_dir / "pipeline.py").write_text('''
from nanoml.components import DataComponent, FeaturesComponent, TrainingComponent

data = DataComponent(
    name="data_ingestion",
    schedule="@daily"
)

features = FeaturesComponent(
    name="feature_generation",
    depends_on=[data],
    schedule="@daily"
)

training = TrainingComponent(
    name="model_training",
    depends_on=[features],
    schedule="@daily"
)
''')

    return tmp_path


def test_full_code_generation_workflow(full_project):
    """End-to-end test: init -> generate -> validate artifacts."""
    import os
    runner = CliRunner()

    # Change to project directory
    old_cwd = os.getcwd()
    os.chdir(full_project)

    try:
        # Run generate
        result = runner.invoke(cli, ["generate", "--clean"])
        assert result.exit_code == 0

        # Verify Flink job
        flink_job = full_project / ".nanoml" / "generated" / "flink" / "streaming_features.py"
        assert flink_job.exists()

        code = flink_job.read_text()
        assert "user_features" in code
        assert "movie_features" in code
        assert "kafka://user_events" in code
        assert "kafka://movie_events" in code
        assert "def main():" in code

        # Verify Feast config
        feast_store = full_project / ".nanoml" / "generated" / "feast" / "feature_store.yaml"
        assert feast_store.exists()

        feast_features = full_project / ".nanoml" / "generated" / "feast" / "features.py"
        assert feast_features.exists()

        features_code = feast_features.read_text()
        assert "user_id = Entity" in features_code
        assert "movie_id = Entity" in features_code
        assert "user_features = FeatureView" in features_code
        assert "movie_features = FeatureView" in features_code

        # Verify Airflow DAG
        airflow_dag = full_project / ".nanoml" / "generated" / "airflow" / "pipeline_dag.py"
        assert airflow_dag.exists()

        dag_code = airflow_dag.read_text()
        assert "data_ingestion" in dag_code
        assert "feature_generation" in dag_code
        assert "model_training" in dag_code
        # Dependencies use variable names
        assert "data >> feature_generation" in dag_code
        assert "features >> model_training" in dag_code
    finally:
        os.chdir(old_cwd)


def test_regeneration_idempotent(full_project):
    """Running generate multiple times produces same output."""
    import os
    runner = CliRunner()

    # Change to project directory
    old_cwd = os.getcwd()
    os.chdir(full_project)

    try:
        # First generation
        result1 = runner.invoke(cli, ["generate"])
        assert result1.exit_code == 0

        flink_job = full_project / ".nanoml" / "generated" / "flink" / "streaming_features.py"
        content1 = flink_job.read_text()

        # Second generation
        result2 = runner.invoke(cli, ["generate"])
        assert result2.exit_code == 0

        content2 = flink_job.read_text()

        # Should be identical
        assert content1 == content2
    finally:
        os.chdir(old_cwd)
