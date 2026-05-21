import sys
from pathlib import Path
from typing import Optional
import pandas as pd
import numpy as np

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
        data_dir = Path(__file__).parent.parent / "data"
        ratings_file = data_dir / "ratings.csv"

        if not ratings_file.exists():
            print("  ⚠ Data not found, downloading first...")
            from data.download import download_movielens
            download_movielens(data_dir)

        print("Computing user features...")

        # Load ratings
        df = pd.read_csv(ratings_file)

        # Compute user-level features
        user_features = df.groupby('userId').agg({
            'rating': ['mean', 'std', 'count'],
            'timestamp': ['min', 'max']
        }).reset_index()

        user_features.columns = ['userId', 'avg_rating', 'rating_std', 'rating_count', 'first_rating_time', 'last_rating_time']

        # Show summary
        print(f"  • User avg rating: {user_features['avg_rating'].mean():.2f} ± {user_features['avg_rating'].std():.2f}")
        print(f"  • User rating count: {user_features['rating_count'].mean():.2f} ± {user_features['rating_count'].std():.2f}")
        print(f"✓ Computed {len(user_features.columns)-1} features for {len(user_features)} users")

        # Save features (simulates feature store)
        features_file = data_dir / "user_features.csv"
        user_features.to_csv(features_file, index=False)

        return user_features
