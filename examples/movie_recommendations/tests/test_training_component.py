import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from components.training import TrainingComponent


def test_training_component_instantiation():
    """TrainingComponent can be instantiated."""
    component = TrainingComponent(name="model_training")
    assert component.name == "model_training"
    assert component.schedule == "@daily"


def test_training_component_has_run_method():
    """TrainingComponent has run method."""
    component = TrainingComponent(name="model_training")
    assert hasattr(component, "run")
    assert callable(component.run)
