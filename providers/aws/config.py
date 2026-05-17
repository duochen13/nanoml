import yaml
import re
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field


# Valid AWS regions (subset for validation)
VALID_REGIONS = [
    "us-east-1", "us-east-2", "us-west-1", "us-west-2",
    "eu-west-1", "eu-west-2", "eu-central-1",
    "ap-southeast-1", "ap-southeast-2", "ap-northeast-1"
]


@dataclass
class AWSConfig:
    """AWS provider configuration."""

    region: str
    account_id: Optional[str] = None
    vpc_cidr: str = "10.0.0.0/16"

    # Service-specific configs
    storage_bucket: Optional[str] = None
    messaging_cluster: Optional[str] = None
    feature_store_prefix: str = "nanoml"
    training_instance_type: str = "ml.m5.xlarge"
    serving_instance_type: str = "ml.t2.medium"
    orchestration_environment: Optional[str] = None

    # Raw service configs
    _services: dict[str, dict] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.region not in VALID_REGIONS:
            raise ValueError(
                f"Invalid region '{self.region}'. "
                f"Must be one of: {', '.join(VALID_REGIONS)}"
            )

        # Set defaults from service configs or use sensible defaults
        if "storage" in self._services:
            self.storage_bucket = self._services["storage"].get("bucket_name")
        elif self.storage_bucket is None:
            # Provide default bucket name
            self.storage_bucket = "nanoml-data"

        if "messaging" in self._services:
            self.messaging_cluster = self._services["messaging"].get("cluster_name")

        if "training" in self._services:
            self.training_instance_type = self._services["training"].get(
                "instance_type", self.training_instance_type
            )

    @classmethod
    def from_file(cls, config_path: Path) -> "AWSConfig":
        """Load AWS config from nanoml.yaml file.

        Args:
            config_path: Path to nanoml.yaml

        Returns:
            AWSConfig instance
        """
        with open(config_path) as f:
            data = yaml.safe_load(f)

        return cls.from_dict(data)

    @classmethod
    def from_yaml(cls, yaml_content: str) -> "AWSConfig":
        """Load AWS config from YAML string.

        Args:
            yaml_content: YAML content as string

        Returns:
            AWSConfig instance
        """
        data = yaml.safe_load(yaml_content)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> "AWSConfig":
        """Load AWS config from dictionary.

        Args:
            data: Configuration dictionary

        Returns:
            AWSConfig instance
        """
        infra = data.get("infrastructure", {})
        aws_config = infra.get("aws", {})

        return cls(
            region=aws_config.get("region", "us-east-1"),
            account_id=aws_config.get("account_id"),
            vpc_cidr=aws_config.get("vpc_cidr", "10.0.0.0/16"),
            _services=aws_config.get("services", {})
        )

    def get_service_config(self, service_name: str) -> dict[str, Any]:
        """Get configuration for a specific service.

        Args:
            service_name: Service name (e.g., "storage", "messaging")

        Returns:
            Service configuration dictionary
        """
        return self._services.get(service_name, {})
