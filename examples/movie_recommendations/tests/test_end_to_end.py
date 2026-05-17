import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


def test_pipeline_module_exists():
    """Pipeline module can be imported."""
    from pipeline import main
    assert callable(main)


def test_all_components_exist():
    """All five components can be imported."""
    from components.data import DataComponent
    from components.features import FeaturesComponent
    from components.training import TrainingComponent
    from components.evaluation import EvaluationComponent
    from components.serving import ServingComponent

    assert DataComponent is not None
    assert FeaturesComponent is not None
    assert TrainingComponent is not None
    assert EvaluationComponent is not None
    assert ServingComponent is not None
