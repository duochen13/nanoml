import pytest
from moto import mock_aws
from providers.aws.clients.feature_store import SageMakerFeatureStoreClient
from providers.aws.clients.training import SageMakerTrainingClient
from providers.aws.clients.model_serving import SageMakerServingClient


@mock_aws
def test_feature_store_create_feature_group():
    """FeatureStoreClient creates feature groups."""
    client = SageMakerFeatureStoreClient(region="us-east-1")

    feature_group_name = client.create_feature_group(
        name="user_features",
        record_identifier="user_id",
        event_time_feature="timestamp",
        features=["age", "country"]
    )

    assert feature_group_name == "user_features"


@mock_aws
def test_training_client_create_job():
    """TrainingClient creates SageMaker training job."""
    client = SageMakerTrainingClient(region="us-east-1")

    job_name = client.create_training_job(
        job_name="test-training",
        algorithm="xgboost",
        instance_type="ml.m5.xlarge",
        input_data_s3="s3://bucket/data",
        output_s3="s3://bucket/output"
    )

    assert job_name == "test-training"


@mock_aws
def test_serving_client_create_endpoint():
    """ServingClient creates SageMaker endpoint."""
    client = SageMakerServingClient(region="us-east-1")

    endpoint_name = client.create_endpoint(
        endpoint_name="test-endpoint",
        model_data_s3="s3://bucket/model.tar.gz",
        instance_type="ml.t2.medium"
    )

    assert endpoint_name == "test-endpoint"


@mock_aws
def test_serving_client_invoke_endpoint():
    """ServingClient invokes endpoint for predictions."""
    client = SageMakerServingClient(region="us-east-1")

    # Create endpoint first
    client.create_endpoint(
        endpoint_name="test-endpoint",
        model_data_s3="s3://bucket/model.tar.gz",
        instance_type="ml.t2.medium"
    )

    # Invoke
    result = client.invoke_endpoint("test-endpoint", {"features": [1, 2, 3]})

    assert result is not None
