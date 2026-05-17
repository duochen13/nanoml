import boto3
from typing import Optional


class MSKMessagingClient:
    """Amazon MSK (Managed Streaming for Kafka) client.

    Implements same interface as local MessagingClient but uses MSK.
    """

    def __init__(self, region: str = "us-east-1"):
        """Initialize MSK client.

        Args:
            region: AWS region
        """
        self.region = region
        self.kafka = boto3.client("kafka", region_name=region)

    def create_cluster(
        self,
        cluster_name: str,
        instance_type: str,
        broker_count: int,
        kafka_version: str = "2.8.1",
        subnets: Optional[list[str]] = None
    ) -> str:
        """Create MSK cluster.

        Args:
            cluster_name: Cluster name
            instance_type: Broker instance type (e.g., kafka.m5.large)
            broker_count: Number of brokers
            kafka_version: Kafka version
            subnets: VPC subnet IDs

        Returns:
            Cluster ARN
        """
        # Note: This is simplified. Real implementation needs VPC/subnet setup.
        response = self.kafka.create_cluster(
            ClusterName=cluster_name,
            KafkaVersion=kafka_version,
            NumberOfBrokerNodes=broker_count,
            BrokerNodeGroupInfo={
                "InstanceType": instance_type,
                "ClientSubnets": subnets or []
            }
        )

        return response["ClusterArn"]

    def list_clusters(self) -> list[dict]:
        """List MSK clusters.

        Returns:
            List of cluster info dictionaries
        """
        response = self.kafka.list_clusters()
        return response.get("ClusterInfoList", [])

    def get_bootstrap_brokers(self, cluster_arn: str) -> str:
        """Get bootstrap broker connection string.

        Args:
            cluster_arn: Cluster ARN

        Returns:
            Bootstrap brokers connection string
        """
        response = self.kafka.get_bootstrap_brokers(ClusterArn=cluster_arn)
        return response["BootstrapBrokerString"]

    def publish(self, topic: str, message: str, cluster_arn: str):
        """Publish message to Kafka topic.

        Args:
            topic: Topic name
            message: Message content
            cluster_arn: MSK cluster ARN
        """
        # Get bootstrap brokers
        brokers = self.get_bootstrap_brokers(cluster_arn)

        # Use kafka-python library (would need to be installed)
        from kafka import KafkaProducer

        producer = KafkaProducer(bootstrap_servers=brokers.split(","))
        producer.send(topic, message.encode())
        producer.flush()

    def consume(self, topic: str, cluster_arn: str, count: int = 1) -> list[str]:
        """Consume messages from Kafka topic.

        Args:
            topic: Topic name
            cluster_arn: MSK cluster ARN
            count: Number of messages to consume

        Returns:
            List of messages
        """
        brokers = self.get_bootstrap_brokers(cluster_arn)

        from kafka import KafkaConsumer

        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=brokers.split(","),
            auto_offset_reset="earliest"
        )

        messages = []
        for msg in consumer:
            messages.append(msg.value.decode())
            if len(messages) >= count:
                break

        consumer.close()
        return messages
