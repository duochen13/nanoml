import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from components.serving import ServingComponent


def test_serving_component_instantiation():
    """ServingComponent can be instantiated."""
    component = ServingComponent(name="model_serving")
    assert component.name == "model_serving"
    assert component.schedule == "@once"


def test_serving_component_has_run_method():
    """ServingComponent has run method."""
    component = ServingComponent(name="model_serving")
    assert hasattr(component, "run")
    assert callable(component.run)


def test_serving_component_has_get_recommendations():
    """ServingComponent has get_recommendations method."""
    component = ServingComponent(name="model_serving")
    assert hasattr(component, "get_recommendations")
    assert callable(component.get_recommendations)
