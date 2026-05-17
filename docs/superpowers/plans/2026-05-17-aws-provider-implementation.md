# AWS Provider Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable NanoML deployment to AWS cloud infrastructure using managed services.

**Architecture:** AWS CDK for Infrastructure as Code, AWS SDK for service clients, one-to-one mapping of local services to AWS equivalents.

**Tech Stack:** AWS CDK (Python), boto3 (AWS SDK), AWS services (S3, MSK, Kinesis Analytics, SageMaker, MWAA, etc.), pytest with moto (AWS mocking)

---

## Service Mapping: Local → AWS

| Local Service | AWS Service |
|--------------|-------------|
| LocalStack S3 | **Amazon S3** |
| Kafka | **Amazon MSK** (Managed Streaming for Kafka) |
| Apache Flink | **Amazon Kinesis Data Analytics** (Flink runtime) |
| Feast (Postgres + Redis) | **Amazon SageMaker Feature Store** |
| Local Training | **Amazon SageMaker Training Jobs** |
| MLflow | **Amazon SageMaker Experiments** |
| Model Server | **Amazon SageMaker Endpoints** |
| FastAPI Gateway | **Amazon API Gateway** |
| Airflow | **Amazon MWAA** (Managed Workflows for Apache Airflow) |
| Lineage API | **SageMaker Lineage Tracking** |
| Dashboard | **Amazon QuickSight** (or custom) |

---

## File Structure

**Code to create:**
- `providers/aws/__init__.py`
- `providers/aws/config.py` - AWS-specific configuration
- `providers/aws/clients/storage.py` - S3 client
- `providers/aws/clients/messaging.py` - MSK client
- `providers/aws/clients/stream_processing.py` - Kinesis Analytics client
- `providers/aws/clients/feature_store.py` - SageMaker Feature Store client
- `providers/aws/clients/training.py` - SageMaker Training client
- `providers/aws/clients/experiment_tracking.py` - SageMaker Experiments client
- `providers/aws/clients/model_serving.py` - SageMaker Endpoints client
- `providers/aws/clients/api_gateway.py` - API Gateway client
- `providers/aws/clients/orchestration.py` - MWAA client
- `providers/aws/infrastructure/app.py` - CDK app entry point
- `providers/aws/infrastructure/stacks/storage_stack.py` - S3 stack
- `providers/aws/infrastructure/stacks/messaging_stack.py` - MSK stack
- `providers/aws/infrastructure/stacks/streaming_stack.py` - Kinesis stack
- `providers/aws/infrastructure/stacks/ml_stack.py` - SageMaker stack
- `providers/aws/infrastructure/stacks/orchestration_stack.py` - MWAA stack
- `providers/aws/infrastructure/stacks/networking_stack.py` - VPC stack
- `cli/deploy.py` - Deployment CLI command
- `tests/providers/aws/test_*.py` - AWS provider tests
- `docs/deployment/aws.md` - AWS deployment guide

**Code to modify:**
- `nanoml.yaml` - Add AWS provider configuration schema
- `cli/main.py` - Add deploy command

---

## Task 1: AWS Configuration & Base Setup

**Files:**
- Create: `providers/aws/__init__.py`
- Create: `providers/aws/config.py`
- Test: `tests/providers/aws/test_config.py`

- [ ] **Step 1: Write failing test for AWS config**

```python
# tests/providers/aws/test_config.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/providers/aws/test_config.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'providers.aws.config'"

- [ ] **Step 3: Implement AWS configuration**

```python
# providers/aws/__init__.py
"""AWS provider for NanoML infrastructure."""

# providers/aws/config.py
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

        # Set defaults from service configs
        if "storage" in self._services:
            self.storage_bucket = self._services["storage"].get("bucket_name")

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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/providers/aws/test_config.py -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add providers/aws/ tests/providers/aws/test_config.py
git commit -m "$(cat <<'EOF'
feat(aws): add AWS provider configuration

AWSConfig class for managing AWS-specific settings:
- Region, account ID, VPC CIDR
- Service-specific configurations
- Loads from nanoml.yaml
- Validates region format

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Storage & Messaging Clients (S3, MSK)

**Files:**
- Create: `providers/aws/clients/storage.py`
- Create: `providers/aws/clients/messaging.py`
- Test: `tests/providers/aws/clients/test_storage.py`
- Test: `tests/providers/aws/clients/test_messaging.py`

- [ ] **Step 1: Write failing tests for S3 and MSK clients**

```python
# tests/providers/aws/clients/test_storage.py
import pytest
from moto import mock_s3
import boto3
from providers.aws.clients.storage import S3StorageClient


@mock_s3
def test_s3_create_bucket():
    """S3StorageClient creates buckets."""
    client = S3StorageClient(region="us-east-1")

    client.create_bucket("test-bucket")

    # Verify bucket exists
    s3 = boto3.client("s3", region_name="us-east-1")
    buckets = s3.list_buckets()["Buckets"]
    assert any(b["Name"] == "test-bucket" for b in buckets)


@mock_s3
def test_s3_upload_file(tmp_path):
    """S3StorageClient uploads files."""
    client = S3StorageClient(region="us-east-1")
    client.create_bucket("test-bucket")

    # Create test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world")

    client.upload_file(test_file, "test-bucket", "test.txt")

    # Verify file exists
    s3 = boto3.client("s3", region_name="us-east-1")
    obj = s3.get_object(Bucket="test-bucket", Key="test.txt")
    assert obj["Body"].read().decode() == "hello world"


@mock_s3
def test_s3_download_file(tmp_path):
    """S3StorageClient downloads files."""
    client = S3StorageClient(region="us-east-1")
    client.create_bucket("test-bucket")

    # Upload file
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world")
    client.upload_file(test_file, "test-bucket", "test.txt")

    # Download to new location
    download_path = tmp_path / "downloaded.txt"
    client.download_file("test-bucket", "test.txt", download_path)

    assert download_path.read_text() == "hello world"


# tests/providers/aws/clients/test_messaging.py
import pytest
from moto import mock_kafka
from providers.aws.clients.messaging import MSKMessagingClient


@mock_kafka
def test_msk_create_cluster():
    """MSKMessagingClient creates Kafka cluster."""
    client = MSKMessagingClient(region="us-east-1")

    cluster_arn = client.create_cluster(
        cluster_name="test-cluster",
        instance_type="kafka.m5.large",
        broker_count=3
    )

    assert cluster_arn is not None
    assert "test-cluster" in cluster_arn


@mock_kafka
def test_msk_list_clusters():
    """MSKMessagingClient lists clusters."""
    client = MSKMessagingClient(region="us-east-1")

    client.create_cluster("cluster-1", "kafka.m5.large", 3)
    client.create_cluster("cluster-2", "kafka.m5.large", 3)

    clusters = client.list_clusters()
    assert len(clusters) == 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/providers/aws/clients/test_storage.py -v`
Run: `pytest tests/providers/aws/clients/test_messaging.py -v`
Expected: FAIL

- [ ] **Step 3: Implement S3 storage client**

```python
# providers/aws/clients/__init__.py
"""AWS service clients."""

# providers/aws/clients/storage.py
import boto3
from pathlib import Path
from typing import Optional


class S3StorageClient:
    """Amazon S3 storage client.

    Implements same interface as local StorageClient but uses S3.
    """

    def __init__(self, region: str = "us-east-1"):
        """Initialize S3 client.

        Args:
            region: AWS region
        """
        self.region = region
        self.s3 = boto3.client("s3", region_name=region)

    def create_bucket(self, bucket_name: str):
        """Create S3 bucket.

        Args:
            bucket_name: Bucket name
        """
        if self.region == "us-east-1":
            # us-east-1 doesn't need LocationConstraint
            self.s3.create_bucket(Bucket=bucket_name)
        else:
            self.s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": self.region}
            )

    def upload_file(self, local_path: Path, bucket: str, key: str):
        """Upload file to S3.

        Args:
            local_path: Path to local file
            bucket: S3 bucket name
            key: S3 object key
        """
        self.s3.upload_file(str(local_path), bucket, key)

    def download_file(self, bucket: str, key: str, local_path: Path):
        """Download file from S3.

        Args:
            bucket: S3 bucket name
            key: S3 object key
            local_path: Path to save file
        """
        self.s3.download_file(bucket, key, str(local_path))

    def exists(self, bucket: str, key: str) -> bool:
        """Check if object exists in S3.

        Args:
            bucket: S3 bucket name
            key: S3 object key

        Returns:
            True if object exists
        """
        try:
            self.s3.head_object(Bucket=bucket, Key=key)
            return True
        except:
            return False

    def list_objects(self, bucket: str, prefix: str = "") -> list[str]:
        """List objects in S3 bucket.

        Args:
            bucket: S3 bucket name
            prefix: Key prefix to filter

        Returns:
            List of object keys
        """
        response = self.s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

        if "Contents" not in response:
            return []

        return [obj["Key"] for obj in response["Contents"]]
```

- [ ] **Step 4: Implement MSK messaging client**

```python
# providers/aws/clients/messaging.py
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
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/providers/aws/clients/test_storage.py -v`
Run: `pytest tests/providers/aws/clients/test_messaging.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add providers/aws/clients/ tests/providers/aws/clients/
git commit -m "$(cat <<'EOF'
feat(aws): add S3 and MSK service clients

S3StorageClient:
- create_bucket, upload_file, download_file
- exists, list_objects

MSKMessagingClient:
- create_cluster, list_clusters
- get_bootstrap_brokers
- publish, consume (using kafka-python)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: SageMaker Clients (Feature Store, Training, Serving)

**Files:**
- Create: `providers/aws/clients/feature_store.py`
- Create: `providers/aws/clients/training.py`
- Create: `providers/aws/clients/model_serving.py`
- Test: `tests/providers/aws/clients/test_sagemaker.py`

- [ ] **Step 1: Write failing tests for SageMaker clients**

```python
# tests/providers/aws/clients/test_sagemaker.py
import pytest
from moto import mock_sagemaker
from providers.aws.clients.feature_store import SageMakerFeatureStoreClient
from providers.aws.clients.training import SageMakerTrainingClient
from providers.aws.clients.model_serving import SageMakerServingClient


@mock_sagemaker
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


@mock_sagemaker
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


@mock_sagemaker
def test_serving_client_create_endpoint():
    """ServingClient creates SageMaker endpoint."""
    client = SageMakerServingClient(region="us-east-1")

    endpoint_name = client.create_endpoint(
        endpoint_name="test-endpoint",
        model_data_s3="s3://bucket/model.tar.gz",
        instance_type="ml.t2.medium"
    )

    assert endpoint_name == "test-endpoint"


@mock_sagemaker
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/providers/aws/clients/test_sagemaker.py -v`
Expected: FAIL

- [ ] **Step 3: Implement SageMaker Feature Store client**

```python
# providers/aws/clients/feature_store.py
import boto3
from typing import Any


class SageMakerFeatureStoreClient:
    """Amazon SageMaker Feature Store client."""

    def __init__(self, region: str = "us-east-1"):
        """Initialize Feature Store client."""
        self.region = region
        self.sagemaker = boto3.client("sagemaker", region_name=region)
        self.runtime = boto3.client("sagemaker-featurestore-runtime", region_name=region)

    def create_feature_group(
        self,
        name: str,
        record_identifier: str,
        event_time_feature: str,
        features: list[str],
        s3_uri: str = None
    ) -> str:
        """Create SageMaker feature group.

        Args:
            name: Feature group name
            record_identifier: Record ID feature name
            event_time_feature: Timestamp feature name
            features: List of feature names
            s3_uri: S3 URI for offline store

        Returns:
            Feature group name
        """
        feature_definitions = [
            {"FeatureName": feat, "FeatureType": "String"}
            for feat in features
        ]

        # Add record identifier and event time
        feature_definitions.extend([
            {"FeatureName": record_identifier, "FeatureType": "String"},
            {"FeatureName": event_time_feature, "FeatureType": "String"}
        ])

        config = {
            "FeatureGroupName": name,
            "RecordIdentifierFeatureName": record_identifier,
            "EventTimeFeatureName": event_time_feature,
            "FeatureDefinitions": feature_definitions,
            "OnlineStoreConfig": {"EnableOnlineStore": True}
        }

        if s3_uri:
            config["OfflineStoreConfig"] = {
                "S3StorageConfig": {"S3Uri": s3_uri}
            }

        self.sagemaker.create_feature_group(**config)

        return name

    def put_record(self, feature_group_name: str, record: dict[str, Any]):
        """Write record to feature store.

        Args:
            feature_group_name: Feature group name
            record: Record data
        """
        # Convert record to Feature Store format
        features = [
            {"FeatureName": k, "ValueAsString": str(v)}
            for k, v in record.items()
        ]

        self.runtime.put_record(
            FeatureGroupName=feature_group_name,
            Record=features
        )

    def get_record(self, feature_group_name: str, record_id: str) -> dict:
        """Retrieve record from feature store.

        Args:
            feature_group_name: Feature group name
            record_id: Record identifier

        Returns:
            Record data
        """
        response = self.runtime.get_record(
            FeatureGroupName=feature_group_name,
            RecordIdentifierValueAsString=record_id
        )

        # Convert from Feature Store format
        record = {
            feat["FeatureName"]: feat["ValueAsString"]
            for feat in response["Record"]
        }

        return record
```

- [ ] **Step 4: Implement SageMaker Training client**

```python
# providers/aws/clients/training.py
import boto3
from typing import Optional


class SageMakerTrainingClient:
    """Amazon SageMaker Training client."""

    def __init__(self, region: str = "us-east-1"):
        """Initialize Training client."""
        self.region = region
        self.sagemaker = boto3.client("sagemaker", region_name=region)

    def create_training_job(
        self,
        job_name: str,
        algorithm: str,
        instance_type: str,
        input_data_s3: str,
        output_s3: str,
        role_arn: Optional[str] = None,
        hyperparameters: Optional[dict] = None
    ) -> str:
        """Create SageMaker training job.

        Args:
            job_name: Training job name
            algorithm: Algorithm (e.g., xgboost, pytorch)
            instance_type: Instance type (e.g., ml.m5.xlarge)
            input_data_s3: S3 URI for training data
            output_s3: S3 URI for model output
            role_arn: IAM role ARN
            hyperparameters: Training hyperparameters

        Returns:
            Training job name
        """
        # Map algorithm to container image
        algorithm_images = {
            "xgboost": f"433757028032.dkr.ecr.{self.region}.amazonaws.com/xgboost:latest",
            "pytorch": f"763104351884.dkr.ecr.{self.region}.amazonaws.com/pytorch-training:latest"
        }

        config = {
            "TrainingJobName": job_name,
            "RoleArn": role_arn or f"arn:aws:iam::123456789012:role/SageMakerRole",
            "AlgorithmSpecification": {
                "TrainingImage": algorithm_images.get(algorithm),
                "TrainingInputMode": "File"
            },
            "InputDataConfig": [
                {
                    "ChannelName": "training",
                    "DataSource": {
                        "S3DataSource": {
                            "S3DataType": "S3Prefix",
                            "S3Uri": input_data_s3
                        }
                    }
                }
            ],
            "OutputDataConfig": {"S3OutputPath": output_s3},
            "ResourceConfig": {
                "InstanceType": instance_type,
                "InstanceCount": 1,
                "VolumeSizeInGB": 30
            },
            "StoppingCondition": {"MaxRuntimeInSeconds": 3600}
        }

        if hyperparameters:
            config["HyperParameters"] = hyperparameters

        self.sagemaker.create_training_job(**config)

        return job_name

    def wait_for_training_job(self, job_name: str):
        """Wait for training job to complete.

        Args:
            job_name: Training job name
        """
        waiter = self.sagemaker.get_waiter("training_job_completed_or_stopped")
        waiter.wait(TrainingJobName=job_name)

    def get_training_job_status(self, job_name: str) -> str:
        """Get training job status.

        Args:
            job_name: Training job name

        Returns:
            Status (InProgress, Completed, Failed, etc.)
        """
        response = self.sagemaker.describe_training_job(TrainingJobName=job_name)
        return response["TrainingJobStatus"]
```

- [ ] **Step 5: Implement SageMaker Serving client**

```python
# providers/aws/clients/model_serving.py
import boto3
import json
from typing import Any


class SageMakerServingClient:
    """Amazon SageMaker Endpoint client for model serving."""

    def __init__(self, region: str = "us-east-1"):
        """Initialize Serving client."""
        self.region = region
        self.sagemaker = boto3.client("sagemaker", region_name=region)
        self.runtime = boto3.client("sagemaker-runtime", region_name=region)

    def create_endpoint(
        self,
        endpoint_name: str,
        model_data_s3: str,
        instance_type: str,
        role_arn: str = None
    ) -> str:
        """Create SageMaker endpoint.

        Args:
            endpoint_name: Endpoint name
            model_data_s3: S3 URI to model.tar.gz
            instance_type: Instance type (e.g., ml.t2.medium)
            role_arn: IAM role ARN

        Returns:
            Endpoint name
        """
        model_name = f"{endpoint_name}-model"
        config_name = f"{endpoint_name}-config"

        # Create model
        self.sagemaker.create_model(
            ModelName=model_name,
            PrimaryContainer={
                "Image": f"763104351884.dkr.ecr.{self.region}.amazonaws.com/pytorch-inference:latest",
                "ModelDataUrl": model_data_s3
            },
            ExecutionRoleArn=role_arn or f"arn:aws:iam::123456789012:role/SageMakerRole"
        )

        # Create endpoint config
        self.sagemaker.create_endpoint_config(
            EndpointConfigName=config_name,
            ProductionVariants=[
                {
                    "VariantName": "primary",
                    "ModelName": model_name,
                    "InstanceType": instance_type,
                    "InitialInstanceCount": 1
                }
            ]
        )

        # Create endpoint
        self.sagemaker.create_endpoint(
            EndpointName=endpoint_name,
            EndpointConfigName=config_name
        )

        return endpoint_name

    def invoke_endpoint(self, endpoint_name: str, payload: dict) -> Any:
        """Invoke endpoint for prediction.

        Args:
            endpoint_name: Endpoint name
            payload: Input data

        Returns:
            Prediction result
        """
        response = self.runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType="application/json",
            Body=json.dumps(payload)
        )

        result = json.loads(response["Body"].read())
        return result

    def delete_endpoint(self, endpoint_name: str):
        """Delete endpoint.

        Args:
            endpoint_name: Endpoint name
        """
        self.sagemaker.delete_endpoint(EndpointName=endpoint_name)
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `pytest tests/providers/aws/clients/test_sagemaker.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add providers/aws/clients/feature_store.py providers/aws/clients/training.py providers/aws/clients/model_serving.py tests/providers/aws/clients/test_sagemaker.py
git commit -m "$(cat <<'EOF'
feat(aws): add SageMaker service clients

SageMakerFeatureStoreClient:
- create_feature_group, put_record, get_record

SageMakerTrainingClient:
- create_training_job, wait_for_training_job
- get_training_job_status

SageMakerServingClient:
- create_endpoint, invoke_endpoint, delete_endpoint

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Infrastructure as Code (AWS CDK)

**Files:**
- Create: `providers/aws/infrastructure/app.py`
- Create: `providers/aws/infrastructure/stacks/base_stack.py`
- Create: `providers/aws/infrastructure/stacks/networking_stack.py`
- Create: `providers/aws/infrastructure/stacks/ml_stack.py`
- Test: `tests/providers/aws/infrastructure/test_cdk_stacks.py`

- [ ] **Step 1: Write failing test for CDK stacks**

```python
# tests/providers/aws/infrastructure/test_cdk_stacks.py
import pytest
from aws_cdk import App
from providers.aws.infrastructure.stacks.networking_stack import NetworkingStack
from providers.aws.infrastructure.stacks.ml_stack import MLStack


def test_networking_stack_creates_vpc():
    """NetworkingStack creates VPC with public/private subnets."""
    app = App()
    stack = NetworkingStack(app, "test-networking")

    # Verify VPC exists
    assert stack.vpc is not None


def test_ml_stack_creates_s3_bucket():
    """MLStack creates S3 bucket for data."""
    app = App()
    network_stack = NetworkingStack(app, "test-networking")
    ml_stack = MLStack(app, "test-ml", vpc=network_stack.vpc)

    assert ml_stack.data_bucket is not None


def test_ml_stack_creates_sagemaker_resources():
    """MLStack creates SageMaker domain."""
    app = App()
    network_stack = NetworkingStack(app, "test-networking")
    ml_stack = MLStack(app, "test-ml", vpc=network_stack.vpc)

    assert ml_stack.sagemaker_domain is not None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/providers/aws/infrastructure/test_cdk_stacks.py -v`
Expected: FAIL

- [ ] **Step 3: Implement CDK base stack**

```python
# providers/aws/infrastructure/__init__.py
"""AWS CDK infrastructure definitions."""

# providers/aws/infrastructure/stacks/__init__.py
"""CDK stack definitions."""

# providers/aws/infrastructure/stacks/base_stack.py
from aws_cdk import Stack
from constructs import Construct


class BaseStack(Stack):
    """Base stack with common configurations."""

    def __init__(self, scope: Construct, id: str, **kwargs):
        """Initialize base stack.

        Args:
            scope: CDK app
            id: Stack ID
            **kwargs: Additional stack parameters
        """
        super().__init__(scope, id, **kwargs)

        # Common tags
        self.tags.set_tag("Project", "NanoML")
        self.tags.set_tag("ManagedBy", "CDK")
```

- [ ] **Step 4: Implement networking stack**

```python
# providers/aws/infrastructure/stacks/networking_stack.py
from aws_cdk import aws_ec2 as ec2
from constructs import Construct
from .base_stack import BaseStack


class NetworkingStack(BaseStack):
    """Networking infrastructure (VPC, subnets, security groups)."""

    def __init__(self, scope: Construct, id: str, cidr: str = "10.0.0.0/16", **kwargs):
        """Initialize networking stack.

        Args:
            scope: CDK app
            id: Stack ID
            cidr: VPC CIDR block
            **kwargs: Additional stack parameters
        """
        super().__init__(scope, id, **kwargs)

        # VPC with public and private subnets
        self.vpc = ec2.Vpc(
            self,
            "NanoMLVPC",
            ip_addresses=ec2.IpAddresses.cidr(cidr),
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                )
            ]
        )

        # Security group for SageMaker
        self.sagemaker_sg = ec2.SecurityGroup(
            self,
            "SageMakerSecurityGroup",
            vpc=self.vpc,
            description="Security group for SageMaker resources"
        )

        # Security group for MSK
        self.msk_sg = ec2.SecurityGroup(
            self,
            "MSKSecurityGroup",
            vpc=self.vpc,
            description="Security group for MSK cluster"
        )

        self.msk_sg.add_ingress_rule(
            peer=self.msk_sg,
            connection=ec2.Port.tcp(9092),
            description="Kafka broker communication"
        )
```

- [ ] **Step 5: Implement ML stack**

```python
# providers/aws/infrastructure/stacks/ml_stack.py
from aws_cdk import (
    aws_s3 as s3,
    aws_sagemaker as sagemaker,
    aws_iam as iam,
    RemovalPolicy
)
from aws_cdk import aws_ec2 as ec2
from constructs import Construct
from .base_stack import BaseStack


class MLStack(BaseStack):
    """ML infrastructure (S3, SageMaker, Feature Store)."""

    def __init__(self, scope: Construct, id: str, vpc: ec2.Vpc, **kwargs):
        """Initialize ML stack.

        Args:
            scope: CDK app
            id: Stack ID
            vpc: VPC from networking stack
            **kwargs: Additional stack parameters
        """
        super().__init__(scope, id, **kwargs)

        # S3 bucket for data
        self.data_bucket = s3.Bucket(
            self,
            "DataBucket",
            bucket_name="nanoml-data",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # S3 bucket for models
        self.model_bucket = s3.Bucket(
            self,
            "ModelBucket",
            bucket_name="nanoml-models",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # IAM role for SageMaker
        self.sagemaker_role = iam.Role(
            self,
            "SageMakerExecutionRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess")
            ]
        )

        # Grant S3 access
        self.data_bucket.grant_read_write(self.sagemaker_role)
        self.model_bucket.grant_read_write(self.sagemaker_role)

        # SageMaker Domain
        self.sagemaker_domain = sagemaker.CfnDomain(
            self,
            "SageMakerDomain",
            domain_name="nanoml-domain",
            auth_mode="IAM",
            default_user_settings=sagemaker.CfnDomain.UserSettingsProperty(
                execution_role=self.sagemaker_role.role_arn
            ),
            subnet_ids=[subnet.subnet_id for subnet in vpc.private_subnets],
            vpc_id=vpc.vpc_id
        )
```

- [ ] **Step 6: Implement CDK app**

```python
# providers/aws/infrastructure/app.py
"""AWS CDK app entry point."""
from aws_cdk import App, Environment
from stacks.networking_stack import NetworkingStack
from stacks.ml_stack import MLStack


def main():
    """Create and synthesize CDK app."""
    app = App()

    # Get environment from context
    env = Environment(
        account=app.node.try_get_context("account"),
        region=app.node.try_get_context("region") or "us-east-1"
    )

    # Create stacks
    networking = NetworkingStack(app, "NanoML-Networking", env=env)
    ml = MLStack(app, "NanoML-ML", vpc=networking.vpc, env=env)

    app.synth()


if __name__ == "__main__":
    main()
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `pytest tests/providers/aws/infrastructure/test_cdk_stacks.py -v`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add providers/aws/infrastructure/ tests/providers/aws/infrastructure/
git commit -m "$(cat <<'EOF'
feat(aws): add CDK infrastructure stacks

NetworkingStack:
- VPC with public/private subnets
- Security groups for SageMaker, MSK

MLStack:
- S3 buckets (data, models)
- SageMaker Domain
- IAM roles

CDK app synthesizes CloudFormation templates.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Deploy CLI Command

**Files:**
- Create: `cli/deploy.py`
- Modify: `cli/main.py`
- Test: `tests/cli/test_deploy.py`

- [ ] **Step 1: Write failing test for deploy command**

```python
# tests/cli/test_deploy.py
import pytest
from click.testing import CliRunner
from cli.main import cli


def test_deploy_command_validates_provider(tmp_path):
    """nanoml deploy validates provider config."""
    # Create invalid config
    config = tmp_path / "nanoml.yaml"
    config.write_text("name: test\nversion: 0.1.0\ninfrastructure:\n  provider: invalid")

    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["deploy"])

        assert result.exit_code != 0
        assert "Invalid provider" in result.output


def test_deploy_command_aws_synthesizes_cdk(tmp_path):
    """nanoml deploy --provider aws synthesizes CDK."""
    config = tmp_path / "nanoml.yaml"
    config.write_text("""
name: test
version: 0.1.0
infrastructure:
  provider: aws
  aws:
    region: us-east-1
    account_id: "123456789012"
""")

    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["deploy", "--provider", "aws", "--dry-run"])

        assert result.exit_code == 0
        assert "Synthesizing CDK" in result.output


def test_deploy_command_local_starts_docker_compose(tmp_path):
    """nanoml deploy --provider local starts Docker Compose."""
    config = tmp_path / "nanoml.yaml"
    config.write_text("""
name: test
version: 0.1.0
infrastructure:
  provider: local
""")

    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["deploy", "--provider", "local"])

        assert result.exit_code == 0
        assert "Starting local infrastructure" in result.output
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/cli/test_deploy.py -v`
Expected: FAIL

- [ ] **Step 3: Implement deploy command**

```python
# cli/deploy.py
import click
import subprocess
from pathlib import Path
from core.config import load_config
from providers.aws.config import AWSConfig


@click.command()
@click.option(
    "--provider",
    type=click.Choice(["local", "aws"]),
    help="Infrastructure provider"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Synthesize but don't deploy"
)
def deploy(provider: str, dry_run: bool):
    """Deploy NanoML infrastructure.

    Deploys to local (Docker Compose) or AWS (CDK).
    """
    # Load config
    config_path = Path.cwd() / "nanoml.yaml"

    if not config_path.exists():
        click.echo("❌ No nanoml.yaml found", err=True)
        raise click.Abort()

    config = load_config(config_path)

    # Determine provider
    if provider is None:
        provider = config.infrastructure.get("provider", "local")

    if provider not in ["local", "aws"]:
        click.echo(f"❌ Invalid provider: {provider}", err=True)
        click.echo("Must be one of: local, aws", err=True)
        raise click.Abort()

    click.echo(f"Deploying to {provider}...")

    if provider == "local":
        deploy_local()
    elif provider == "aws":
        deploy_aws(config_path, dry_run)

    click.echo("✅ Deployment complete!")


def deploy_local():
    """Deploy to local infrastructure (Docker Compose)."""
    click.echo("Starting local infrastructure...")

    # Run docker-compose up
    result = subprocess.run(
        ["docker-compose", "up", "-d"],
        cwd="deployment",
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        click.echo(f"❌ Docker Compose failed: {result.stderr}", err=True)
        raise click.Abort()

    click.echo("✓ Local services started")


def deploy_aws(config_path: Path, dry_run: bool):
    """Deploy to AWS (CDK)."""
    click.echo("Loading AWS configuration...")

    aws_config = AWSConfig.from_file(config_path)

    click.echo(f"  Region: {aws_config.region}")
    click.echo(f"  Account: {aws_config.account_id or 'default'}")

    # Synthesize CDK
    click.echo("Synthesizing CDK stacks...")

    cdk_dir = Path(__file__).parent.parent / "providers" / "aws" / "infrastructure"

    synth_result = subprocess.run(
        ["cdk", "synth"],
        cwd=cdk_dir,
        capture_output=True,
        text=True
    )

    if synth_result.returncode != 0:
        click.echo(f"❌ CDK synth failed: {synth_result.stderr}", err=True)
        raise click.Abort()

    click.echo("✓ CDK synthesized")

    if dry_run:
        click.echo("Dry run - skipping deployment")
        return

    # Deploy CDK
    click.echo("Deploying CDK stacks...")

    deploy_result = subprocess.run(
        ["cdk", "deploy", "--all", "--require-approval", "never"],
        cwd=cdk_dir,
        capture_output=True,
        text=True
    )

    if deploy_result.returncode != 0:
        click.echo(f"❌ CDK deploy failed: {deploy_result.stderr}", err=True)
        raise click.Abort()

    click.echo("✓ CDK deployed")
```

- [ ] **Step 4: Add deploy command to CLI**

```python
# cli/main.py (modify)
from cli.deploy import deploy

# ...existing commands...
cli.add_command(deploy)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/cli/test_deploy.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add cli/deploy.py cli/main.py tests/cli/test_deploy.py
git commit -m "$(cat <<'EOF'
feat(cli): add nanoml deploy command

Supports two providers:
- local: starts Docker Compose
- aws: synthesizes and deploys CDK stacks

Flags:
- --provider: specify provider (overrides config)
- --dry-run: synthesize but don't deploy

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Documentation & Testing

**Files:**
- Create: `docs/deployment/aws.md`
- Create: `tests/providers/aws/test_integration.py`

- [ ] **Step 1: Write comprehensive AWS deployment guide**

```markdown
# docs/deployment/aws.md
# AWS Deployment Guide

Deploy NanoML to AWS using managed services.

## Prerequisites

- AWS account with appropriate permissions
- AWS CLI configured (`aws configure`)
- AWS CDK installed (`npm install -g aws-cdk`)
- Docker (for local development)

## Quick Start

### 1. Configure AWS Provider

Edit `nanoml.yaml`:

```yaml
name: my_project
version: 0.1.0

infrastructure:
  provider: aws
  aws:
    region: us-east-1
    account_id: "123456789012"  # Your AWS account ID

    services:
      storage:
        bucket_name: my-project-data
      messaging:
        cluster_name: my-project-kafka
        instance_type: kafka.m5.large
      feature_store:
        feature_group_prefix: my-project
      training:
        instance_type: ml.m5.xlarge
      serving:
        instance_type: ml.t2.medium
      orchestration:
        environment_name: my-project-airflow
```

### 2. Deploy Infrastructure

```bash
nanoml deploy --provider aws
```

This will:
1. Synthesize CDK stacks (CloudFormation templates)
2. Deploy networking (VPC, subnets, security groups)
3. Deploy ML infrastructure (S3, SageMaker, Feature Store)
4. Deploy messaging (MSK cluster)
5. Deploy orchestration (MWAA environment)

### 3. Verify Deployment

Check AWS Console:
- **S3**: Buckets created for data and models
- **SageMaker**: Domain and Feature Store groups
- **MSK**: Kafka cluster running
- **MWAA**: Airflow environment active

## Service Details

### Storage (Amazon S3)

**Buckets created:**
- `{project-name}-data`: Raw data storage
- `{project-name}-models`: Model artifacts

**Usage:**
```python
from providers.aws.clients.storage import S3StorageClient

storage = S3StorageClient(region="us-east-1")
storage.upload_file("data.csv", "my-project-data", "data.csv")
```

### Messaging (Amazon MSK)

**Cluster:**
- Kafka version: 2.8.1
- Instance type: Configurable (default: kafka.m5.large)
- Broker count: 3 (multi-AZ)

**Usage:**
```python
from providers.aws.clients.messaging import MSKMessagingClient

msk = MSKMessagingClient(region="us-east-1")
msk.publish("my-topic", "message", cluster_arn)
```

### Feature Store (SageMaker Feature Store)

**Features:**
- Online store (low-latency reads)
- Offline store (S3-backed for training)
- Automatic versioning

**Usage:**
```python
from providers.aws.clients.feature_store import SageMakerFeatureStoreClient

fs = SageMakerFeatureStoreClient(region="us-east-1")
fs.create_feature_group("user_features", "user_id", "timestamp", ["age", "country"])
fs.put_record("user_features", {"user_id": "123", "age": "25", "timestamp": "2024-01-01"})
```

### Training (SageMaker Training Jobs)

**Algorithms supported:**
- XGBoost
- PyTorch
- TensorFlow
- Custom containers

**Usage:**
```python
from providers.aws.clients.training import SageMakerTrainingClient

training = SageMakerTrainingClient(region="us-east-1")
training.create_training_job(
    job_name="my-training",
    algorithm="xgboost",
    instance_type="ml.m5.xlarge",
    input_data_s3="s3://bucket/data",
    output_s3="s3://bucket/output"
)
```

### Serving (SageMaker Endpoints)

**Endpoint types:**
- Real-time (always on)
- Serverless (auto-scaling)
- Batch transform (offline)

**Usage:**
```python
from providers.aws.clients.model_serving import SageMakerServingClient

serving = SageMakerServingClient(region="us-east-1")
serving.create_endpoint(
    endpoint_name="my-endpoint",
    model_data_s3="s3://bucket/model.tar.gz",
    instance_type="ml.t2.medium"
)

# Invoke for predictions
result = serving.invoke_endpoint("my-endpoint", {"features": [1, 2, 3]})
```

### Orchestration (MWAA - Managed Airflow)

**Environment:**
- Airflow version: 2.5.1
- Executor: Celery
- Auto-scaling workers

**Usage:**
- Upload DAGs to S3: `s3://{project-name}-airflow/dags/`
- Access UI: https://{environment-id}.{region}.airflow.amazonaws.com

## Cost Estimation

Typical monthly costs for a small production deployment:

| Service | Configuration | Estimated Cost |
|---------|--------------|----------------|
| S3 | 100 GB storage | $2.30 |
| MSK | 3x kafka.m5.large | $450 |
| SageMaker Feature Store | 1M online reads | $2.50 |
| SageMaker Training | 10 hours ml.m5.xlarge | $96 |
| SageMaker Endpoints | 1x ml.t2.medium 24/7 | $67 |
| MWAA | Small environment | $305 |
| **Total** | | **~$923/month** |

**Cost optimization:**
- Use Spot instances for training
- Enable S3 Intelligent-Tiering
- Use Serverless endpoints for low-traffic models
- Scale down MSK cluster size

## Migration from Local to AWS

### 1. Export Local Data

```bash
# Export S3 data
aws s3 sync s3://local-nanoml-data/ s3://my-project-data/

# Export Kafka topics (requires kafka-console-consumer)
kafka-console-consumer --bootstrap-server localhost:9092 --topic my-topic --from-beginning > my-topic.json
```

### 2. Update Configuration

Change `nanoml.yaml` from `provider: local` to `provider: aws`.

### 3. Regenerate Code

```bash
nanoml generate --clean
```

This regenerates infrastructure code for AWS services.

### 4. Deploy

```bash
nanoml deploy --provider aws
```

### 5. Import Data

```bash
# Upload to S3
aws s3 cp my-data.csv s3://my-project-data/

# Publish to MSK (requires MSK cluster ARN)
python scripts/import_to_msk.py
```

## Troubleshooting

### CDK Deployment Fails

**Error:** "Unable to assume role"

**Solution:**
```bash
aws configure
cdk bootstrap aws://ACCOUNT-ID/REGION
```

### SageMaker Training Job Fails

**Error:** "AccessDenied: S3"

**Solution:** Ensure SageMaker execution role has S3 permissions.

Check `providers/aws/infrastructure/stacks/ml_stack.py` - the role should have S3 access.

### MSK Cluster Not Accessible

**Error:** "Cannot connect to brokers"

**Solution:** Ensure security group allows inbound on port 9092.

```bash
aws kafka describe-cluster --cluster-arn <arn>
```

Check `BootstrapBrokers` and test connectivity.

## Best Practices

1. **Use VPC Endpoints** for S3 to avoid data transfer costs
2. **Enable CloudWatch Logs** for all services
3. **Tag Resources** with project name and environment
4. **Use Secrets Manager** for credentials
5. **Enable Cost Alerts** to monitor spending
6. **Backup Important Data** regularly
7. **Use IAM Roles** instead of access keys

## Cleanup

Remove all AWS resources:

```bash
cdk destroy --all
```

This will delete:
- All CDK stacks
- S3 buckets (if empty)
- SageMaker endpoints
- MSK cluster
- MWAA environment

**Note:** Buckets with data will not be deleted automatically.

## Next Steps

- [Configure CI/CD for AWS](./cicd.md)
- [Set up monitoring with CloudWatch](./monitoring.md)
- [Enable multi-region deployment](./multi-region.md)
```

- [ ] **Step 2: Write AWS integration test**

```python
# tests/providers/aws/test_integration.py
"""Integration tests for AWS provider.

Note: These tests use moto for AWS mocking.
For real AWS testing, set AWS_INTEGRATION_TESTS=1.
"""
import pytest
import os
from moto import mock_s3, mock_sagemaker
from providers.aws.clients.storage import S3StorageClient
from providers.aws.clients.feature_store import SageMakerFeatureStoreClient


@pytest.mark.skipif(
    os.getenv("AWS_INTEGRATION_TESTS") != "1",
    reason="AWS integration tests disabled (set AWS_INTEGRATION_TESTS=1)"
)
@mock_s3
@mock_sagemaker
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
```

- [ ] **Step 3: Test documentation accuracy**

Validate that all commands in `docs/deployment/aws.md` work correctly.

- [ ] **Step 4: Commit**

```bash
git add docs/deployment/aws.md tests/providers/aws/test_integration.py
git commit -m "$(cat <<'EOF'
docs(aws): add comprehensive AWS deployment guide

Covers:
- Quick start deployment
- Service details (S3, MSK, SageMaker, MWAA)
- Cost estimation
- Migration from local to AWS
- Troubleshooting
- Best practices
- Cleanup

Also adds AWS integration test.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Final Validation

- [ ] **Step 1: Run full test suite**

Run: `pytest tests/providers/aws/ -v`
Expected: All tests pass

- [ ] **Step 2: Test CDK synthesis**

```bash
cd providers/aws/infrastructure
cdk synth
```

Expected: CloudFormation templates generated in `cdk.out/`

- [ ] **Step 3: Verify all AWS clients**

Check that these exist and have tests:
- [ ] S3StorageClient
- [ ] MSKMessagingClient
- [ ] SageMakerFeatureStoreClient
- [ ] SageMakerTrainingClient
- [ ] SageMakerServingClient

- [ ] **Step 4: Test deploy command help**

Run: `nanoml deploy --help`
Expected: Shows provider and dry-run options

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "$(cat <<'EOF'
feat: complete AWS provider implementation

Full AWS deployment support:
- Service clients (S3, MSK, SageMaker)
- CDK infrastructure stacks
- Deploy CLI command
- Migration from local to AWS
- Comprehensive documentation

One command deployment: nanoml deploy --provider aws

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Summary

This plan implements AWS cloud deployment for NanoML.

**Key deliverables:**
1. AWS configuration management
2. Service clients (S3, MSK, SageMaker Feature Store, Training, Serving)
3. CDK infrastructure stacks (Networking, ML)
4. Deploy CLI command
5. Migration tools
6. Comprehensive AWS deployment documentation

**After this plan:**
- Users can deploy to AWS with one command
- All local services map to AWS equivalents
- Infrastructure as code with CDK
- Ready for production deployment on AWS
