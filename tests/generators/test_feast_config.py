import pytest
import yaml
from pathlib import Path
from generators.feast_config import FeastConfigGenerator


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
'''


def test_parse_generates_feast_entities_and_features(tmp_path):
    """parse_source() extracts entities and features for Feast."""
    features_file = tmp_path / "definitions.py"
    features_file.write_text(SAMPLE_FEATURES)

    gen = FeastConfigGenerator()
    parsed = gen.parse_source(features_file)

    assert "entities" in parsed
    assert "feature_views" in parsed

    # Should extract user_id entity
    assert len(parsed["entities"]) == 1
    assert parsed["entities"][0]["name"] == "user_id"

    # Should extract user_features view
    assert len(parsed["feature_views"]) == 1
    view = parsed["feature_views"][0]
    assert view["name"] == "user_features"
    assert view["entity"] == "user_id"
    assert len(view["features"]) == 2


def test_generate_feast_store_yaml(tmp_path):
    """generate_code() produces feature_store.yaml."""
    features_file = tmp_path / "definitions.py"
    features_file.write_text(SAMPLE_FEATURES)

    gen = FeastConfigGenerator(output_type="store")
    parsed = gen.parse_source(features_file)
    code = gen.generate_code(parsed)

    # Should be valid YAML
    config = yaml.safe_load(code)

    assert config["project"] == "nanorec"
    assert config["provider"] == "local"
    assert "online_store" in config
    assert "offline_store" in config


def test_generate_feast_features_py(tmp_path):
    """generate_code() produces features.py with Entity and FeatureView."""
    features_file = tmp_path / "definitions.py"
    features_file.write_text(SAMPLE_FEATURES)

    gen = FeastConfigGenerator(output_type="features")
    parsed = gen.parse_source(features_file)
    code = gen.generate_code(parsed)

    # Should be valid Python
    compile(code, "<string>", "exec")

    # Should define entities
    assert "Entity(" in code
    assert 'name="user_id"' in code

    # Should define feature views
    assert "FeatureView(" in code
    assert 'name="user_features"' in code


def test_get_output_paths(tmp_path):
    """get_output_path() returns correct paths for store vs features."""
    gen_store = FeastConfigGenerator(output_type="store")
    assert gen_store.get_output_path(tmp_path) == \
        tmp_path / ".nanorec" / "generated" / "feast" / "feature_store.yaml"

    gen_features = FeastConfigGenerator(output_type="features")
    assert gen_features.get_output_path(tmp_path) == \
        tmp_path / ".nanorec" / "generated" / "feast" / "features.py"
