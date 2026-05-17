import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class TrainingComponent:
    """Trains recommendation model.

    Responsibilities:
    1. Fetch features from Feast
    2. Train ML model (Random Forest for demo)
    3. Log model and metrics to MLflow
    """

    def __init__(self, name: str, depends_on: Optional[list] = None, schedule: Optional[str] = None):
        """Initialize training component.

        Args:
            name: Component name
            depends_on: Dependencies
            schedule: Cron schedule
        """
        self.name = name
        self.depends_on = depends_on or []
        self.schedule = schedule or "@daily"

    def run(self):
        """Run model training."""
        print(f"✓ Model training would run here")
        print(f"  (Simplified implementation for demo)")
        # In full implementation:
        # - Fetch features from Feast
        # - Train Random Forest model
        # - Log to MLflow
