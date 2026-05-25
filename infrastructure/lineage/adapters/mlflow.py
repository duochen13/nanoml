"""MLflow adapter with monitoring."""

from typing import Dict, Any, List
from datetime import datetime
from .base import MLAdapter, HealthCheck, HealthStatus, Metric


class MLflowAdapter(MLAdapter):
    """Adapter for MLflow tracking server."""

    def __init__(self, tracking_uri: str, model_name: str = None):
        """Initialize MLflow adapter.

        Args:
            tracking_uri: MLflow tracking server URI (can be web UI URL or API base URL)
            model_name: Optional model name to monitor
        """
        # Extract base URL if full web UI URL is provided
        # e.g., http://localhost:5001/#/experiments/... -> http://localhost:5001
        if "/#/" in tracking_uri:
            base_url = tracking_uri.split("/#/")[0]
        elif "?" in tracking_uri and "#" not in tracking_uri:
            base_url = tracking_uri.split("?")[0]
        else:
            base_url = tracking_uri.rstrip("/")

        super().__init__(
            component_id=f"mlflow_{model_name or 'server'}",
            component_name=model_name or "MLflow Server",
            component_type="mlflow_server"
        )
        self.tracking_uri = base_url
        self.model_name = model_name
        self._client = None

    def _get_client(self):
        """Get or create MLflow client."""
        if self._client is None:
            try:
                import mlflow as mlflow_module
                from mlflow import MlflowClient as Client
                mlflow_module.set_tracking_uri(self.tracking_uri)
                self._client = Client()
            except ImportError as e:
                print(f"MLflow import error: {e}")
                return None
            except Exception as e:
                print(f"MLflow client error: {e}")
                return None
        return self._client

    async def health_check(self) -> HealthCheck:
        """Check MLflow server health."""
        try:
            client = self._get_client()
            if client is None:
                return HealthCheck(
                    status=HealthStatus.UNKNOWN,
                    message="mlflow not available",
                    checked_at=datetime.utcnow(),
                    details={}
                )

            # Try to list experiments as health check
            experiments = client.search_experiments(max_results=1)

            return HealthCheck(
                status=HealthStatus.HEALTHY,
                message="MLflow server accessible",
                checked_at=datetime.utcnow(),
                details={
                    "tracking_uri": self.tracking_uri,
                    "experiments_count": len(experiments)
                }
            )
        except Exception as e:
            return HealthCheck(
                status=HealthStatus.UNHEALTHY,
                message=f"MLflow server not accessible: {str(e)}",
                checked_at=datetime.utcnow(),
                details={"error": str(e)}
            )

    async def get_metrics(self) -> List[Metric]:
        """Collect MLflow metrics."""
        metrics = []
        timestamp = datetime.utcnow()

        try:
            client = self._get_client()

            # Count experiments
            experiments = client.search_experiments()
            metrics.append(Metric(
                name="experiments_count",
                value=len(experiments),
                unit="count",
                timestamp=timestamp,
                labels={"tracking_uri": self.tracking_uri}
            ))

            # If model name specified, get model versions
            if self.model_name:
                try:
                    versions = client.search_model_versions(f"name='{self.model_name}'")
                    metrics.append(Metric(
                        name="model_versions_count",
                        value=len(versions),
                        unit="count",
                        timestamp=timestamp,
                        labels={"model_name": self.model_name}
                    ))
                except:
                    pass

        except Exception as e:
            print(f"Error collecting MLflow metrics: {e}")

        return metrics

    async def get_metadata(self) -> Dict[str, Any]:
        """Get MLflow metadata."""
        metadata = {
            "tracking_uri": self.tracking_uri,
            "model_name": self.model_name,
        }

        try:
            client = self._get_client()

            if client is None:
                metadata["error"] = "MLflow client could not be created (import failed)"
                return metadata

            # Get experiments with details
            experiments = client.search_experiments()
            metadata["experiments_count"] = len(experiments)
            metadata["experiments"] = [
                {
                    "experiment_id": exp.experiment_id,
                    "name": exp.name,
                    "artifact_location": exp.artifact_location,
                    "lifecycle_stage": exp.lifecycle_stage,
                    "tags": exp.tags
                }
                for exp in experiments
            ]

            # Get registered models
            registered_models = client.search_registered_models()
            metadata["registered_models_count"] = len(registered_models)
            metadata["registered_models"] = [
                {
                    "name": model.name,
                    "creation_timestamp": model.creation_timestamp,
                    "last_updated_timestamp": model.last_updated_timestamp,
                    "description": model.description,
                    "tags": model.tags
                }
                for model in registered_models
            ]

            if self.model_name:
                # Get model details
                try:
                    model = client.get_registered_model(self.model_name)
                    metadata["model_description"] = model.description
                    metadata["model_tags"] = model.tags
                except:
                    pass

        except Exception as e:
            metadata["error"] = str(e)

        return metadata

    async def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        if not self.model_name:
            return {"error": "No model name specified"}

        try:
            client = self._get_client()

            # Get registered model
            model = client.get_registered_model(self.model_name)

            # Get latest versions
            versions = client.search_model_versions(f"name='{self.model_name}'")

            # Sort by version number
            versions = sorted(versions, key=lambda v: int(v.version), reverse=True)

            return {
                "name": model.name,
                "description": model.description,
                "tags": model.tags,
                "creation_timestamp": model.creation_timestamp,
                "last_updated_timestamp": model.last_updated_timestamp,
                "latest_versions": [
                    {
                        "version": v.version,
                        "stage": v.current_stage,
                        "run_id": v.run_id,
                        "status": v.status
                    }
                    for v in versions[:5]
                ]
            }

        except Exception as e:
            return {"error": str(e)}

    async def get_predictions_count(self) -> int:
        """Get prediction count (requires custom tracking).

        Note: MLflow doesn't track predictions by default.
        This would need custom instrumentation.
        """
        # Placeholder - would need custom metrics
        return 0
