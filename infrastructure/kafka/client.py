"""Kafka client wrapper."""

from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic
from typing import List, Dict, Any
import json


class KafkaClient:
    """Client for interacting with Kafka."""

    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        """Initialize Kafka client."""
        self.bootstrap_servers = bootstrap_servers
        self.admin = KafkaAdminClient(bootstrap_servers=bootstrap_servers)

    def create_topic(self, name: str, num_partitions: int = 1, replication_factor: int = 1) -> None:
        """Create Kafka topic."""
        topic = NewTopic(
            name=name,
            num_partitions=num_partitions,
            replication_factor=replication_factor
        )
        try:
            self.admin.create_topics([topic])
        except Exception:
            pass  # Topic may already exist

    def list_topics(self) -> List[str]:
        """List all Kafka topics."""
        return list(self.admin.list_topics())

    def delete_topic(self, name: str) -> None:
        """Delete Kafka topic."""
        self.admin.delete_topics([name])

    def create_producer(self) -> KafkaProducer:
        """Create Kafka producer."""
        return KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def create_consumer(self, topic: str, group_id: str) -> KafkaConsumer:
        """Create Kafka consumer."""
        return KafkaConsumer(
            topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda v: json.loads(v.decode('utf-8'))
        )
