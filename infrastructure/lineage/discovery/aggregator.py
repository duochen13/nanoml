"""Discovery aggregator that combines all discovery sources."""

from typing import List, Dict, Any
from .base import DiscoveredComponent
from .docker import DockerDiscovery
from .aws import AWSDiscovery
from .gcp import GCPDiscovery


class DiscoveryAggregator:
    """Aggregates discoveries from multiple sources."""

    def __init__(
        self,
        aws_region: str = None,
        aws_profile: str = None,
        gcp_project: str = None,
        gcp_location: str = "us-central1"
    ):
        """Initialize discovery aggregator.

        Args:
            aws_region: AWS region
            aws_profile: AWS profile name
            gcp_project: GCP project ID
            gcp_location: GCP location/region
        """
        self.discoveries = [
            DockerDiscovery(),
            AWSDiscovery(region=aws_region, profile=aws_profile),
            GCPDiscovery(project_id=gcp_project, location=gcp_location),
        ]

    async def discover_all(self) -> Dict[str, Any]:
        """Run all discoveries and aggregate results.

        Returns:
            Dictionary with discovered components grouped by provider
        """
        all_components = []
        provider_stats = {}

        for discovery in self.discoveries:
            try:
                if discovery.is_available():
                    components = await discovery.discover()
                    all_components.extend(components)

                    # Track stats by provider
                    provider = discovery.__class__.__name__.replace("Discovery", "").lower()
                    provider_stats[provider] = {
                        "available": True,
                        "count": len(components)
                    }
                else:
                    provider = discovery.__class__.__name__.replace("Discovery", "").lower()
                    provider_stats[provider] = {
                        "available": False,
                        "count": 0
                    }
            except Exception as e:
                provider = discovery.__class__.__name__.replace("Discovery", "").lower()
                provider_stats[provider] = {
                    "available": False,
                    "count": 0,
                    "error": str(e)
                }

        # Convert components to dict
        components_dict = [comp.to_dict() for comp in all_components]

        # Group by category
        by_category = {}
        for comp in components_dict:
            category = comp["category"]
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(comp)

        return {
            "components": components_dict,
            "by_category": by_category,
            "stats": {
                "total_components": len(all_components),
                "providers": provider_stats
            }
        }
