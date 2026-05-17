import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class EvaluationComponent:
    """Evaluates trained models.

    Responsibilities:
    1. Load latest model from MLflow
    2. Run evaluation on test set
    3. Log evaluation metrics
    """

    def __init__(self, name: str, depends_on: Optional[list] = None, schedule: Optional[str] = None):
        """Initialize evaluation component."""
        self.name = name
        self.depends_on = depends_on or []
        self.schedule = schedule or "@daily"

    def run(self):
        """Run model evaluation."""
        print(f"✓ Model evaluation would run here")
        print(f"  (Simplified implementation for demo)")
        # In full implementation:
        # - Load model from MLflow
        # - Evaluate on test set
        # - Log metrics
