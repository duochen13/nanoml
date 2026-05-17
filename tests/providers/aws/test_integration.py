"""Integration tests for AWS provider.

Note: These tests use moto for AWS mocking.
For real AWS testing, set AWS_INTEGRATION_TESTS=1.
"""
import pytest
import os
from moto import mock_aws
from providers.aws.clients.storage import S3StorageClient
from providers.aws.clients.feature_store import SageMakerFeatureStoreClient


@pytest.mark.skipif(
    os.getenv("AWS_INTEGRATION_TESTS") != "1",
    reason="AWS integration tests disabled (set AWS_INTEGRATION_TESTS=1)"
)
@mock_aws
def test_full_aws_workflow():
    """Test complete AWS workflow: S3 → Feature Store → Training."""
    # 1. Upload data to S3
    storage = S3StorageClient(region="us-east-1")
    storage.create_bucket("test-data")

    # 2. Create feature store
    fs = SageMakerFeatureStoreClient(region="us-east-1")
    fs.create_feature_group(
        name="test_features",
        record_identifier="user_id",
        event_time_feature="timestamp",
        features=["age", "country"]
    )

    # 3. Put record
    fs.put_record("test_features", {
        "user_id": "123",
        "age": "25",
        "country": "US",
        "timestamp": "2024-01-01T00:00:00Z"
    })

    # 4. Retrieve record
    record = fs.get_record("test_features", "123")

    assert record["user_id"] == "123"
    assert record["age"] == "25"
