import pytest
from pathlib import Path
from generators.airflow_dag import AirflowDAGGenerator


SAMPLE_COMPONENTS = '''
from nanorec.components import DataComponent, FeaturesComponent

data = DataComponent(
    name="data_ingestion",
    schedule="@daily"
)

features = FeaturesComponent(
    name="feature_generation",
    depends_on=[data],
    schedule="@daily"
)
'''


def test_parse_component_dag(tmp_path):
    """parse_source() extracts component DAG structure."""
    components_file = tmp_path / "pipeline.py"
    components_file.write_text(SAMPLE_COMPONENTS)

    gen = AirflowDAGGenerator()
    parsed = gen.parse_source(components_file)

    assert len(parsed["components"]) == 2

    # Check data component
    data = parsed["components"][0]
    assert data["name"] == "data_ingestion"
    assert data["type"] == "DataComponent"
    assert data["schedule"] == "@daily"
    assert data["depends_on"] == []

    # Check features component
    features = parsed["components"][1]
    assert features["name"] == "feature_generation"
    assert features["type"] == "FeaturesComponent"
    assert features["depends_on"] == ["data"]


def test_generate_airflow_dag_code(tmp_path):
    """generate_code() produces valid Airflow DAG."""
    components_file = tmp_path / "pipeline.py"
    components_file.write_text(SAMPLE_COMPONENTS)

    gen = AirflowDAGGenerator()
    parsed = gen.parse_source(components_file)
    code = gen.generate_code(parsed)

    # Should be valid Python
    compile(code, "<string>", "exec")

    # Should import Airflow
    assert "from airflow import DAG" in code

    # Should create tasks
    assert "data_ingestion" in code
    assert "feature_generation" in code

    # Should set dependencies
    assert ">>" in code or "set_downstream" in code


def test_get_output_path(tmp_path):
    """get_output_path() returns .nanorec/generated/airflow/pipeline_dag.py."""
    gen = AirflowDAGGenerator()
    output = gen.get_output_path(tmp_path)

    assert output == tmp_path / ".nanorec" / "generated" / "airflow" / "pipeline_dag.py"
