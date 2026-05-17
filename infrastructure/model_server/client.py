"""Model server client."""

import requests
from typing import List, Dict, Any


class ModelServerClient:
    """Client for interacting with model serving endpoint."""

    def __init__(self, base_url: str = "http://localhost:8001"):
        """Initialize model server client."""
        self.base_url = base_url

    def predict(self, features: List[List[float]], model_name: str = "default") -> List[float]:
        """
        Make predictions.

        Args:
            features: Input features
            model_name: Model to use

        Returns:
            Predictions
        """
        response = requests.post(
            f"{self.base_url}/predict",
            json={"features": features, "model_name": model_name}
        )
        response.raise_for_status()
        return response.json()["predictions"]

    def list_models(self) -> List[str]:
        """List available models."""
        response = requests.get(f"{self.base_url}/models")
        response.raise_for_status()
        return response.json()["models"]
