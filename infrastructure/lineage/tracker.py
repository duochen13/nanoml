"""SHALLOW: Basic lineage tracker."""

from typing import Dict, Any, Optional


class LineageTracker:
    """Basic lineage tracker."""

    def __init__(self, db_path: str = "/data/lineage.db"):
        """Initialize lineage tracker."""
        self.db_path = db_path

    def track_artifact(self, name: str, artifact_type: str, path: Optional[str] = None) -> int:
        """Track an artifact."""
        # SHALLOW: No-op for MVP
        return 1

    def track_lineage(self, source_id: int, target_id: int, relation: str) -> None:
        """Track lineage relationship."""
        # SHALLOW: No-op for MVP
        pass
