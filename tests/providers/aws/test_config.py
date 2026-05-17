import pytest
from pathlib import Path
from providers.aws.config import AWSConfig


SAMPLE_AWS_CONFIG = """
name: test_project
version: 0.1.0

infrastructure:
  provider: aws
  aws:
    region: us-east-1
    account_id: "123456789012"
    vpc_cidr: "10.0.0.0/16"

    services:
      storage:
        bucket_name: nanoml-data
      messaging:
        cluster_name: nanoml-kafka
        instance_type: kafka.m5.large
      feature_store:
        feature_group_prefix: nanoml
      training:
        instance_type: ml.m5.xlarge
      serving:
        instance_type: ml.t2.medium
      orchestration:
        environment_name: nanoml-airflow
"""


def test_load_aws_config(tmp_path):
    """AWSConfig loads from nanoml.yaml."""
    config_file = tmp_path / "nanoml.yaml"
    config_file.write_text(SAMPLE_AWS_CONFIG)

    config = AWSConfig.from_file(config_file)

    assert config.region == "us-east-1"
    assert config.account_id == "123456789012"
    assert config.vpc_cidr == "10.0.0.0/16"


def test_aws_config_defaults():
    """AWSConfig provides sensible defaults."""
    config = AWSConfig(region="us-west-2")

    assert config.region == "us-west-2"
    assert config.vpc_cidr == "10.0.0.0/16"  # Default
    assert config.storage_bucket is not None


def test_aws_config_validates_region():
    """AWSConfig validates AWS region format."""
    with pytest.raises(ValueError, match="Invalid region"):
        AWSConfig(region="invalid-region-123")


def test_aws_config_service_settings():
    """AWSConfig provides service-specific settings."""
    config_file = Path("nanoml.yaml")
    # Use sample config
    config = AWSConfig.from_yaml(SAMPLE_AWS_CONFIG)

    assert config.get_service_config("storage")["bucket_name"] == "nanoml-data"
    assert config.get_service_config("messaging")["cluster_name"] == "nanoml-kafka"
    assert config.get_service_config("training")["instance_type"] == "ml.m5.xlarge"
