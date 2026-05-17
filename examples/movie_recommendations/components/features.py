import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class FeaturesComponent:
    """Computes features using Flink and Feast.

    Responsibilities:
    1. Submit generated Flink streaming job
    2. Apply Feast feature definitions
    3. Monitor feature computation
    """

    def __init__(self, name: str, depends_on: Optional[list] = None, schedule: Optional[str] = None):
        """Initialize features component.

        Args:
            name: Component name
            depends_on: Dependencies (for Airflow DAG)
            schedule: Cron schedule
        """
        self.name = name
        self.depends_on = depends_on or []
        self.schedule = schedule or "@daily"

    def run(self):
        """Run feature computation."""
        print(f"✓ Feature computation would run here")
        print(f"  (Simplified implementation for demo)")
        # In full implementation:
        # - Submit Flink job from .nanorec/generated/flink/
        # - Apply Feast definitions from .nanorec/generated/feast/
