"""GCP resource discovery service."""

import os
from typing import List, Optional
from .base import BaseDiscovery, DiscoveredComponent, ComponentCategory

try:
    from google.cloud import storage, aiplatform
    from google.auth import default
    from google.auth.exceptions import DefaultCredentialsError
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False


class GCPDiscovery(BaseDiscovery):
    """Discover ML components from GCP services."""

    def __init__(self, project_id: Optional[str] = None, location: str = "us-central1"):
        """Initialize GCP discovery.

        Args:
            project_id: GCP project ID (defaults to GOOGLE_CLOUD_PROJECT env var)
            location: GCP region/location
        """
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location

    def is_available(self) -> bool:
        """Check if GCP credentials are configured."""
        if not GCP_AVAILABLE:
            return False

        try:
            credentials, project = default()
            if not self.project_id:
                self.project_id = project
            return True
        except DefaultCredentialsError:
            return False

    async def discover(self) -> List[DiscoveredComponent]:
        """Discover GCP resources.

        Returns:
            List of discovered GCP components
        """
        if not self.is_available():
            return []

        components = []

        try:
            # Discover Cloud Storage buckets
            components.extend(await self._discover_storage())

            # Discover Vertex AI endpoints
            components.extend(await self._discover_vertex_ai())

            # Discover Dataproc clusters
            components.extend(await self._discover_dataproc())

        except Exception as e:
            print(f"Error discovering GCP resources: {e}")

        return components

    async def _discover_storage(self) -> List[DiscoveredComponent]:
        """Discover Cloud Storage buckets."""
        components = []

        try:
            storage_client = storage.Client(project=self.project_id)
            buckets = storage_client.list_buckets()

            for bucket in buckets:
                # Check if bucket name suggests ML data
                is_ml_related = any(keyword in bucket.name.lower()
                                   for keyword in ["data", "ml", "model", "train", "feature"])

                if is_ml_related:
                    components.append(DiscoveredComponent(
                        id=f"gcs_{bucket.name}",
                        name=bucket.name,
                        type="gcs_bucket",
                        provider="gcp",
                        category=ComponentCategory.DATA_SOURCES,
                        metadata={
                            "location": bucket.location,
                            "storage_class": bucket.storage_class,
                            "created_at": bucket.time_created.isoformat() if bucket.time_created else None,
                        }
                    ))

        except Exception as e:
            print(f"Error discovering GCS buckets: {e}")

        return components

    async def _discover_vertex_ai(self) -> List[DiscoveredComponent]:
        """Discover Vertex AI endpoints."""
        components = []

        try:
            aiplatform.init(project=self.project_id, location=self.location)
            endpoints = aiplatform.Endpoint.list()

            for endpoint in endpoints:
                components.append(DiscoveredComponent(
                    id=f"vertex_{endpoint.resource_name.split('/')[-1]}",
                    name=endpoint.display_name,
                    type="vertex_ai_endpoint",
                    provider="gcp",
                    category=ComponentCategory.SERVING,
                    metadata={
                        "resource_name": endpoint.resource_name,
                        "create_time": endpoint.create_time.isoformat() if endpoint.create_time else None,
                        "deployed_models": len(endpoint.deployed_models) if endpoint.deployed_models else 0,
                    }
                ))

        except Exception as e:
            print(f"Error discovering Vertex AI endpoints: {e}")

        return components

    async def _discover_dataproc(self) -> List[DiscoveredComponent]:
        """Discover Dataproc (Spark) clusters."""
        components = []

        try:
            from google.cloud import dataproc_v1

            client = dataproc_v1.ClusterControllerClient(
                client_options={"api_endpoint": f"{self.location}-dataproc.googleapis.com:443"}
            )

            # List clusters in the project and region
            request = dataproc_v1.ListClustersRequest(
                project_id=self.project_id,
                region=self.location
            )

            clusters = client.list_clusters(request=request)

            for cluster in clusters:
                components.append(DiscoveredComponent(
                    id=f"dataproc_{cluster.cluster_name}",
                    name=cluster.cluster_name,
                    type="dataproc_cluster",
                    provider="gcp",
                    category=ComponentCategory.PROCESSING,
                    metadata={
                        "status": cluster.status.state.name,
                        "zone": cluster.config.gce_cluster_config.zone_uri.split("/")[-1] if cluster.config.gce_cluster_config else None,
                    }
                ))

        except Exception as e:
            print(f"Error discovering Dataproc clusters: {e}")

        return components
