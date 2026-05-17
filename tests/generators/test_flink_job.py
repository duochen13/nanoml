import pytest
from pathlib import Path
from generators.flink_job import FlinkJobGenerator


SAMPLE_FEATURES = '''
from nanorec.features import Feature, FeatureGroup

user_features = FeatureGroup(
    name="user_features",
    entity="user_id",
    features=[
        Feature("age", "int"),
        Feature("country", "string"),
    ],
    source="kafka://user_events"
)

item_features = FeatureGroup(
    name="item_features",
    entity="item_id",
    features=[
        Feature("category", "string"),
        Feature("price", "float"),
    ],
    source="kafka://item_events"
)
'''


def test_parse_feature_definitions(tmp_path):
    """parse_source() extracts FeatureGroup definitions."""
    features_file = tmp_path / "definitions.py"
    features_file.write_text(SAMPLE_FEATURES)

    gen = FlinkJobGenerator()
    parsed = gen.parse_source(features_file)

    assert len(parsed["feature_groups"]) == 2

    # Check user_features
    user_fg = parsed["feature_groups"][0]
    assert user_fg["name"] == "user_features"
    assert user_fg["entity"] == "user_id"
    assert user_fg["source"] == "kafka://user_events"
    assert len(user_fg["features"]) == 2
    assert user_fg["features"][0]["name"] == "age"
    assert user_fg["features"][0]["type"] == "int"

    # Check item_features
    item_fg = parsed["feature_groups"][1]
    assert item_fg["name"] == "item_features"
    assert item_fg["entity"] == "item_id"


def test_generate_flink_job_code(tmp_path):
    """generate_code() produces valid Flink job Python code."""
    features_file = tmp_path / "definitions.py"
    features_file.write_text(SAMPLE_FEATURES)

    gen = FlinkJobGenerator()
    parsed = gen.parse_source(features_file)
    code = gen.generate_code(parsed)

    # Should be valid Python
    compile(code, "<string>", "exec")

    # Should import Flink
    assert "from pyflink" in code

    # Should have Kafka source for each feature group
    assert "kafka://user_events" in code
    assert "kafka://item_events" in code

    # Should write to Feast
    assert "feast" in code.lower()


def test_get_output_path(tmp_path):
    """get_output_path() returns .nanorec/generated/flink/streaming_features.py."""
    gen = FlinkJobGenerator()
    output = gen.get_output_path(tmp_path)

    assert output == tmp_path / ".nanorec" / "generated" / "flink" / "streaming_features.py"


def test_full_flink_generation(tmp_path):
    """run() generates complete Flink job."""
    features_file = tmp_path / "definitions.py"
    features_file.write_text(SAMPLE_FEATURES)

    gen = FlinkJobGenerator()
    output_path = gen.run(features_file, tmp_path)

    assert output_path.exists()
    code = output_path.read_text()

    # Verify generated code structure
    assert "def main():" in code
    assert "kafka://user_events" in code
    assert "kafka://item_events" in code
