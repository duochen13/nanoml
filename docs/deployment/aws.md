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
