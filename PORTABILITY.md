# Write Once, Run Anywhere

A core principle of NanoML: **Your Python code works everywhere without modification.**

## The Same Code Runs:

```python
# data/loader.py - Works everywhere!
def load_data(path):
    return pd.read_csv(path)

# features/definitions.py - Works everywhere!
@feature
def user_avg_rating(events):
    return events.groupby('user_id')['rating'].mean()

# training/model.py - Works everywhere!
class RecommenderModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.embedding = nn.Embedding(10000, 128)

    def forward(self, x):
        return self.embedding(x)
```

This exact code runs:
- ✅ On your laptop (local mode)
- ✅ In Docker (local testing)
- ✅ On AWS (deployed)
- ✅ On GCP (deployed)
- ✅ On Azure (deployed)

## How It Works

### Environment Detection

The framework automatically detects where it's running:

```python
# infrastructure/storage/client.py
class StorageClient:
    def __init__(self):
        if os.getenv('AWS_REGION'):
            self.backend = S3Backend()      # Cloud
        elif os.getenv('LOCALSTACK_HOST'):
            self.backend = LocalStackBackend()  # Docker
        else:
            self.backend = FilesystemBackend()  # Local
```

### Graceful Degradation

When services aren't available, the framework falls back gracefully:

```python
# components/data.py
try:
    kafka.send(event)
    print("✓ Event published to Kafka")
except ConnectionError:
    print("⚠ Kafka not available, logging locally")
    logger.info(event)
```

### Unified Interface

You always use the same API:

```python
# Your code - works everywhere
storage.upload('data.csv', 'bucket/path')
kafka.publish('events', data)
mlflow.log_metric('accuracy', 0.95)

# Framework handles the backend:
# - Local: filesystem, console, SQLite
# - Cloud: S3, Kafka, MLflow server
```

## Example: Data Pipeline

### Your Code (Unchanged)

```python
# components/data.py
class DataComponent:
    def run(self, data_dir):
        # Load data
        df = pd.read_csv(data_dir / "ratings.csv")

        # Upload to storage
        self.storage.upload(df, "datasets/ratings")

        # Publish events
        for event in self._create_events(df):
            self.kafka.publish("rating_events", event)

        print("✓ Data pipeline complete")
```

### What Happens Locally

```
1. Read CSV from local disk
2. storage.upload() → Saves to ./data/ratings.parquet
3. kafka.publish() → Prints to console
4. ✓ Data pipeline complete
```

### What Happens in Cloud

```
1. Read CSV from local disk (or S3)
2. storage.upload() → Uploads to s3://prod-bucket/datasets/ratings
3. kafka.publish() → Publishes to Kafka cluster
4. ✓ Data pipeline complete
```

**Same code, different backends - fully automatic.**

## Development Workflow

### Step 1: Develop Locally (Fast)

```bash
make setup
make run  # Uses local filesystem, no infrastructure
```

Your code runs in seconds, instant feedback loop.

### Step 2: Test with Infrastructure (Optional)

```bash
make infra-up  # Start Docker services
python3 pipeline.py  # Now uses Kafka, MLflow, etc.
```

Same code, now with real services - verify integrations work.

### Step 3: Deploy to Cloud (Production)

```bash
nanoml deploy  # Deploy to AWS/GCP/Azure
```

**Same code** now runs on cloud infrastructure at scale.

## Configuration, Not Code Changes

The only thing that changes is configuration:

### config.yaml (Local)
```yaml
environment: local
storage:
  type: filesystem
  path: ./data
```

### config.yaml (Cloud)
```yaml
environment: aws
storage:
  type: s3
  bucket: my-prod-bucket
  region: us-east-1
```

**Your Python code stays identical.**

## Benefits

### 🚀 Productivity
- Develop locally (fast iteration)
- Deploy to cloud (production scale)
- No code rewrites

### 🛡️ Confidence
- Test locally first
- Same code in production
- No surprises

### 🔄 Portability
- Switch clouds easily (AWS → GCP)
- Run anywhere (laptop, server, cloud)
- Not locked into one provider

### 🧪 Testability
- Unit tests run locally (fast)
- Integration tests use Docker
- Production uses real cloud

## What You Control

You write business logic:
```python
# features/definitions.py
@feature
def user_watch_time(events):
    return events.groupby('user_id')['duration'].sum()
```

Framework handles infrastructure:
- Local: Python aggregation in-memory
- Cloud: Distributed processing with Flink

## What Framework Handles

### Automatically Adapted:
- ✅ Storage (filesystem → S3 → GCS → Azure Blob)
- ✅ Messaging (console → Kafka)
- ✅ Feature store (in-memory → Feast)
- ✅ Experiment tracking (SQLite → MLflow server)
- ✅ Orchestration (sequential → Airflow → Cloud Composer)
- ✅ Model serving (in-process → containerized → serverless)

### Always The Same:
- ✅ Your Python code
- ✅ Feature definitions
- ✅ Model architecture
- ✅ Training logic
- ✅ Serving logic

## Anti-Pattern: Environment-Specific Code

❌ **DON'T DO THIS:**
```python
if environment == 'local':
    storage = FilesystemStorage()
elif environment == 'aws':
    storage = S3Storage()
```

✅ **DO THIS:**
```python
storage = get_storage()  # Framework figures it out
storage.upload(data)     # Works everywhere
```

## Summary

**Write once, run anywhere** means:

1. **Same code** - No modifications needed
2. **Same API** - Unified interface for all services
3. **Automatic detection** - Framework handles environment
4. **Graceful fallback** - Works without infrastructure
5. **Configuration-driven** - Change behavior via config, not code

Result: **Develop locally, deploy to cloud, zero code changes.**

This is the power of NanoML - infrastructure abstraction that just works.
