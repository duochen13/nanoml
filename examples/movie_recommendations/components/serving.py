import sys
from pathlib import Path
from typing import Optional, List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class ServingComponent:
    """Deploys and serves recommendation model.

    Responsibilities:
    1. Load model from MLflow
    2. Deploy to model server
    3. Expose via API gateway
    4. Serve predictions
    """

    def __init__(self, name: str, depends_on: Optional[list] = None, schedule: Optional[str] = None):
        """Initialize serving component."""
        self.name = name
        self.depends_on = depends_on or []
        self.schedule = schedule or "@once"  # Deploy once
        self.model = None

    def run(self):
        """Deploy model for serving."""
        print(f"✓ Model serving would be deployed here")
        print(f"  (Simplified implementation for demo)")
        # In full implementation:
        # - Load model from MLflow
        # - Deploy to model server
        # - Register API endpoint

    def get_recommendations(self, user_id: int, top_k: int = 10) -> List[Dict]:
        """Get top-K movie recommendations for user.

        Args:
            user_id: User ID
            top_k: Number of recommendations

        Returns:
            List of recommended movie IDs with scores
        """
        # Simplified demo implementation
        print(f"✓ Getting {top_k} recommendations for user {user_id}")
        return [
            {"movie_id": i, "predicted_rating": 4.5 - (i * 0.1)}
            for i in range(1, top_k + 1)
        ]
