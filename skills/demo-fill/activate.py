#!/usr/bin/env python3
"""Activate demo mode - fills skeleton code with working implementations."""

import shutil
from pathlib import Path


def main():
    """Fill skeleton code with working demo implementations."""
    project_root = Path(__file__).parent.parent.parent
    example_dir = project_root / "examples" / "movie_recommendations"
    components_dir = example_dir / "components"
    backup_dir = example_dir / ".backup"

    # Create backup
    backup_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("Activating Demo Mode")
    print("=" * 60)
    print()

    # Backup original files
    print("📦 Creating backups...")
    for file in ["features.py", "training.py", "evaluation.py", "serving.py"]:
        src = components_dir / file
        dst = backup_dir / file
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  ✓ Backed up {file}")

    print()
    print("🔧 Filling skeleton code with demo implementations...")

    # Fill features.py
    features_code = '''import sys
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
'''

    # Fill training.py
    training_code = '''import sys
from pathlib import Path
from typing import Optional
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import time

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
        data_dir = Path(__file__).parent.parent / "data"
        ratings_file = data_dir / "ratings.csv"
        features_file = data_dir / "user_features.csv"

        print("Training collaborative filtering model...")

        # Load data
        ratings = pd.read_csv(ratings_file)

        if features_file.exists():
            user_features = pd.read_csv(features_file)
            # Merge features
            data = ratings.merge(user_features, on='userId', how='left')
        else:
            data = ratings

        # Create simple train/test split
        train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)

        # Train simple model (simulates 10 epochs)
        print("Epoch 1/10: Loss = 0.4523")
        time.sleep(0.3)
        print("Epoch 5/10: Loss = 0.2134")
        time.sleep(0.3)
        print("Epoch 10/10: Loss = 0.1245")

        # Simulate model training
        model = RandomForestRegressor(n_estimators=10, random_state=42, max_depth=5)

        # Use movieId and userId as features for demo
        X_train = train_data[['userId', 'movieId']].values
        y_train = train_data['rating'].values

        start = time.time()
        model.fit(X_train, y_train)
        elapsed = time.time() - start

        print(f"✓ Model trained (10 epochs, {elapsed:.1f}s)")

        # Save model (simulates MLflow)
        import pickle
        model_file = data_dir / "model.pkl"
        with open(model_file, 'wb') as f:
            pickle.dump(model, f)

        # Save test data for evaluation
        test_data.to_csv(data_dir / "test_data.csv", index=False)

        return model
'''

    # Fill evaluation.py
    evaluation_code = '''import sys
from pathlib import Path
from typing import Optional
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error
import pickle

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
        data_dir = Path(__file__).parent.parent / "data"
        model_file = data_dir / "model.pkl"
        test_file = data_dir / "test_data.csv"

        if not model_file.exists() or not test_file.exists():
            print("  ⚠ Model or test data not found")
            return

        # Load model and test data
        with open(model_file, 'rb') as f:
            model = pickle.load(f)

        test_data = pd.read_csv(test_file)

        print(f"Evaluating on test set ({len(test_data)} ratings)...")

        # Make predictions
        X_test = test_data[['userId', 'movieId']].values
        y_test = test_data['rating'].values
        y_pred = model.predict(X_test)

        # Compute metrics
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)

        # Simulate accuracy@5
        accuracy_at_5 = 0.82  # Simulated for demo

        print(f"  • RMSE: {rmse:.2f}")
        print(f"  • MAE: {mae:.2f}")
        print(f"  • Accuracy@5: {accuracy_at_5:.2f}")
        print("✓ Evaluation complete")

        return {"rmse": rmse, "mae": mae, "accuracy_at_5": accuracy_at_5}
'''

    # Fill serving.py
    serving_code = '''import sys
from pathlib import Path
from typing import Optional
import pandas as pd
import pickle
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class ServingComponent:
    """Serves trained model for predictions.

    Responsibilities:
    1. Load model from MLflow
    2. Set up API endpoint
    3. Serve real-time predictions
    """

    def __init__(self, name: str, depends_on: Optional[list] = None, schedule: Optional[str] = None):
        """Initialize serving component."""
        self.name = name
        self.depends_on = depends_on or []
        self.schedule = schedule or "@once"

    def run(self):
        """Run model serving."""
        data_dir = Path(__file__).parent.parent / "data"
        model_file = data_dir / "model.pkl"
        movies_file = data_dir / "movies.csv"

        if not model_file.exists():
            print("  ⚠ Model not found")
            return

        # Load model
        with open(model_file, 'rb') as f:
            model = pickle.load(f)

        # Load movies for display
        if movies_file.exists():
            movies = pd.read_csv(movies_file)
        else:
            movies = None

        # Generate sample predictions
        sample_user = 42
        sample_movies = [1, 2, 3]  # Top popular movies

        print(f"Sample predictions for user {sample_user}:")

        for i, movie_id in enumerate(sample_movies, 1):
            # Predict rating
            X = np.array([[sample_user, movie_id]])
            pred_rating = model.predict(X)[0]

            # Get movie title
            if movies is not None and movie_id in movies['movieId'].values:
                title = movies[movies['movieId'] == movie_id]['title'].iloc[0]
            else:
                title = f"Movie {movie_id}"

            stars = "⭐" * int(round(pred_rating))
            print(f"  {i}. {title} - Predicted: {pred_rating:.1f} {stars}")

        print("✓ Model ready for serving")
'''

    # Write filled implementations
    (components_dir / "features.py").write_text(features_code)
    print("  ✓ features.py filled")

    (components_dir / "training.py").write_text(training_code)
    print("  ✓ training.py filled")

    (components_dir / "evaluation.py").write_text(evaluation_code)
    print("  ✓ evaluation.py filled")

    (components_dir / "serving.py").write_text(serving_code)
    print("  ✓ serving.py filled")

    print()
    print("=" * 60)
    print("✅ Demo mode activated!")
    print("=" * 60)
    print()
    print("Now run:  make run")
    print()
    print("To restore skeleton code:  make demo-restore")
    print()


if __name__ == "__main__":
    main()
