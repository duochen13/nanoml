import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from components.features import FeaturesComponent


def test_features_component_instantiation():
    """FeaturesComponent can be instantiated."""
    component = FeaturesComponent(name="feature_computation")
    assert component.name == "feature_computation"
    assert component.schedule == "@daily"


def test_features_component_has_run_method():
    """FeaturesComponent has run method."""
    component = FeaturesComponent(name="feature_computation")
    assert hasattr(component, "run")
    assert callable(component.run)
