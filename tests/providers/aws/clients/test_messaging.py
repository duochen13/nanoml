import pytest
from moto import mock_aws
from providers.aws.clients.messaging import MSKMessagingClient


@mock_aws
def test_msk_create_cluster():
    """MSKMessagingClient creates Kafka cluster."""
    client = MSKMessagingClient(region="us-east-1")

    cluster_arn = client.create_cluster(
        cluster_name="test-cluster",
        instance_type="kafka.m5.large",
        broker_count=3
    )

    assert cluster_arn is not None
    assert cluster_arn.startswith("arn:aws:kafka:")


@mock_aws
def test_msk_list_clusters():
    """MSKMessagingClient lists clusters."""
    client = MSKMessagingClient(region="us-east-1")

    client.create_cluster("cluster-1", "kafka.m5.large", 3)
    client.create_cluster("cluster-2", "kafka.m5.large", 3)

    clusters = client.list_clusters()
    assert len(clusters) == 2
