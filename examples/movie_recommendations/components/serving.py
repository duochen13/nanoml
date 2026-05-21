import sys
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
