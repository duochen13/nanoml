"""MLflow client wrapper."""

import mlflow
from mlflow import MlflowClient as BaseMlflowClient
from typing import List, Dict, Any, Optional


class MLflowClient:
    """Client for interacting with MLflow tracking server."""

    def __init__(self, tracking_uri: str = "http://localhost:5001"):
        """Initialize MLflow client."""
        mlflow.set_tracking_uri(tracking_uri)
        self.client = BaseMlflowClient(tracking_uri=tracking_uri)

    def list_experiments(self) -> List[Dict[str, Any]]:
        """List all experiments."""
        experiments = self.client.search_experiments()
        return [
            {
                "id": exp.experiment_id,
                "name": exp.name,
                "artifact_location": exp.artifact_location
            }
            for exp in experiments
        ]

    def create_experiment(self, name: str) -> str:
        """Create new experiment."""
        return self.client.create_experiment(name)

    def log_metric(self, run_id: str, key: str, value: float, step: int = 0) -> None:
        """Log metric to MLflow."""
        self.client.log_metric(run_id, key, value, step=step)

    def log_param(self, run_id: str, key: str, value: Any) -> None:
        """Log parameter to MLflow."""
        self.client.log_param(run_id, key, str(value))

    def start_run(self, experiment_id: str, run_name: Optional[str] = None):
        """Start MLflow run."""
        return mlflow.start_run(experiment_id=experiment_id, run_name=run_name)
