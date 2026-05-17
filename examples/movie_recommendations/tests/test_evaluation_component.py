import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from components.evaluation import EvaluationComponent


def test_evaluation_component_instantiation():
    """EvaluationComponent can be instantiated."""
    component = EvaluationComponent(name="model_evaluation")
    assert component.name == "model_evaluation"
    assert component.schedule == "@daily"


def test_evaluation_component_has_run_method():
    """EvaluationComponent has run method."""
    component = EvaluationComponent(name="model_evaluation")
    assert hasattr(component, "run")
    assert callable(component.run)
