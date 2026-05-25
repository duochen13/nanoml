# Component Monitoring & Abstraction Layer

## Overview

The abstraction layer provides a unified interface for monitoring and managing discovered infrastructure components. Each component type (S3, MLflow, Docker, etc.) gets wrapped with standardized capabilities:

- **Health Checks**: Is the component accessible and healthy?
- **Metrics Collection**: CPU, memory, storage, throughput, etc.
- **Metadata Retrieval**: Configuration, tags, labels
- **Observability**: Logs, traces, performance data

## Architecture

```
┌─────────────────────────────────────┐
│     Frontend (Lineage + Monitor)    │
└─────────────────────────────────────┘
                 ▼
┌─────────────────────────────────────┐
│    Component Abstraction Layer      │
│  • S3Adapter                        │
│  • MLflowAdapter                    │
│  • DockerContainerAdapter           │
│  • SparkAdapter (coming soon)       │
└─────────────────────────────────────┘
                 ▼
┌─────────────────────────────────────┐
│         Raw Infrastructure          │
│  AWS / GCP / Docker / Kubernetes    │
└─────────────────────────────────────┘
```

## API Usage

### 1. Register Components

Register components you want to monitor:

**S3 Bucket:**
```bash
curl -X POST http://localhost:9000/monitor/register \
  -H "Content-Type: application/json" \
  -d '{
    "component_type": "s3_bucket",
    "config": {
      "bucket_name": "ml-data-prod",
      "region": "us-west-2",
      "prefix": "features/"
    }
  }'
```

**MLflow Server:**
```bash
# Option 1: Pass base URL directly
curl -X POST http://localhost:9000/monitor/register \
  -H "Content-Type: application/json" \
  -d '{
    "component_type": "mlflow_server",
    "config": {
      "tracking_uri": "http://localhost:5001",
      "model_name": "recommendation_model"
    }
  }'

# Option 2: Pass full web UI URL (adapter will extract base URL)
curl -X POST http://localhost:9000/monitor/register \
  -H "Content-Type: application/json" \
  -d '{
    "component_type": "mlflow_server",
    "config": {
      "tracking_uri": "http://localhost:5001/#/experiments/258199515700643735",
      "model_name": "recommendation_model"
    }
  }'
```

**Docker Container:**
```bash
curl -X POST http://localhost:9000/monitor/register \
  -H "Content-Type": application/json" \
  -d '{
    "component_type": "docker_container",
    "config": {
      "container_id": "abc123def456",
      "container_name": "spark-master",
      "image": "bitnami/spark:latest"
    }
  }'
```

**Response Format:**

When you register a component, the API returns the complete component details including health status, metrics, and metadata. For example, registering an MLflow server returns:

```json
{
  "status": "registered",
  "type": "mlflow_server",
  "component": {
    "id": "mlflow_server",
    "name": "MLflow Server",
    "type": "mlflow_server",
    "health": {
      "status": "healthy",
      "message": "MLflow server accessible",
      "checked_at": "2026-05-23T09:22:31.666363",
      "details": {
        "tracking_uri": "http://localhost:5001",
        "experiments_count": 6
      }
    },
    "metrics": [
      {
        "name": "experiments_count",
        "value": 6,
        "unit": "count",
        "timestamp": "2026-05-23T09:22:31.666367",
        "labels": {
          "tracking_uri": "http://localhost:5001"
        }
      }
    ],
    "metadata": {
      "tracking_uri": "http://localhost:5001",
      "model_name": null,
      "experiments_count": 6,
      "experiments": [
        {
          "experiment_id": "258199515700643735",
          "name": "movie_recommendations",
          "artifact_location": "mlflow-artifacts:/258199515700643735",
          "lifecycle_stage": "active",
          "tags": {}
        },
        {
          "experiment_id": "837701527473609417",
          "name": "book_recommendations_hybrid_svd_xgboost",
          "artifact_location": "file:///path/to/mlruns/837701527473609417",
          "lifecycle_stage": "active",
          "tags": {}
        }
      ],
      "registered_models_count": 1,
      "registered_models": [
        {
          "name": "movie_recommender",
          "creation_timestamp": 1779354150880,
          "last_updated_timestamp": 1779354150901,
          "description": "",
          "tags": {}
        }
      ]
    }
  }
}
```

### 2. Get Health Status

Check health of all components:

```bash
curl http://localhost:9000/monitor/health
```

Response:
```json
{
  "overall_status": "healthy",
  "components": {
    "s3_ml-data-prod": {
      "name": "ml-data-prod",
      "type": "s3_bucket",
      "status": "healthy",
      "message": "Bucket accessible",
      "checked_at": "2024-01-15T10:30:00Z",
      "details": {
        "bucket": "ml-data-prod",
        "region": "us-west-2"
      }
    },
    "mlflow_recommendation_model": {
      "name": "recommendation_model",
      "type": "mlflow_server",
      "status": "healthy",
      "message": "MLflow server accessible",
      "checked_at": "2024-01-15T10:30:00Z",
      "details": {
        "tracking_uri": "http://localhost:5001",
        "experiments_count": 3
      }
    }
  },
  "summary": {
    "total": 2,
    "healthy": 2,
    "degraded": 0,
    "unhealthy": 0,
    "unknown": 0
  }
}
```

### 3. Collect Metrics

Get metrics from all components:

```bash
curl http://localhost:9000/monitor/metrics
```

Response:
```json
{
  "components": {
    "s3_ml-data-prod": {
      "name": "ml-data-prod",
      "type": "s3_bucket",
      "metrics": [
        {
          "name": "storage_size",
          "value": 1073741824,
          "unit": "bytes",
          "timestamp": "2024-01-15T10:30:00Z",
          "labels": {"bucket": "ml-data-prod"}
        },
        {
          "name": "object_count",
          "value": 1250,
          "unit": "count",
          "timestamp": "2024-01-15T10:30:00Z",
          "labels": {"bucket": "ml-data-prod"}
        }
      ]
    },
    "docker_spark-master": {
      "name": "spark-master",
      "type": "docker_container",
      "metrics": [
        {
          "name": "cpu_usage_percent",
          "value": 45.2,
          "unit": "percent",
          "timestamp": "2024-01-15T10:30:00Z",
          "labels": {"container": "spark-master"}
        },
        {
          "name": "memory_usage_bytes",
          "value": 2147483648,
          "unit": "bytes",
          "timestamp": "2024-01-15T10:30:00Z",
          "labels": {"container": "spark-master"}
        }
      ]
    }
  },
  "collected_at": "2024-01-15T10:30:00Z"
}
```

### 4. Get Component Detail

Get detailed info for a specific component:

```bash
curl http://localhost:9000/monitor/components/s3_ml-data-prod
```

Response:
```json
{
  "id": "s3_ml-data-prod",
  "name": "ml-data-prod",
  "type": "s3_bucket",
  "health": {
    "status": "healthy",
    "message": "Bucket accessible",
    "checked_at": "2024-01-15T10:30:00Z",
    "details": {"bucket": "ml-data-prod", "region": "us-west-2"}
  },
  "metrics": [
    {"name": "storage_size", "value": 1073741824, "unit": "bytes", ...},
    {"name": "object_count", "value": 1250, "unit": "count", ...}
  ],
  "metadata": {
    "bucket_name": "ml-data-prod",
    "region": "us-west-2",
    "prefix": "features/",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

## Component Types

### DataSourceAdapter (S3, GCS, Databases)

Methods:
- `health_check()` - Check accessibility
- `get_metrics()` - Storage size, object count
- `get_schema()` - Infer data schema
- `get_size_bytes()` - Total size

### ProcessingAdapter (Spark, Flink, Docker)

Methods:
- `health_check()` - Check if running
- `get_metrics()` - CPU, memory usage
- `get_job_status()` - Current job state
- `get_logs(limit)` - Recent logs

### MLAdapter (MLflow, Model Servers)

Methods:
- `health_check()` - Server accessibility
- `get_metrics()` - Model count, versions
- `get_model_info()` - Model metadata
- `get_predictions_count()` - Serving metrics

## Use Cases

### 1. Schema Change Detection

Monitor S3 buckets for schema drift:

```python
# Register bucket
await monitor.register_s3_bucket("ml-data-prod", "us-west-2")

# Get schema
adapter = monitor.components["s3_ml-data-prod"]
schema = await adapter.get_schema()

# Compare with previous schema
if schema != previous_schema:
    alert("Schema changed in ml-data-prod!")
```

### 2. Resource Monitoring Dashboard

Build a dashboard showing:
- Which components are healthy
- CPU/memory usage for containers
- Storage size trends for data sources
- Model version deployment status

### 3. Impact Analysis with Health

Combine lineage + monitoring:
```
If S3 bucket is unhealthy:
  → Show downstream models affected
  → Display health status propagation
  → Alert owners of impacted pipelines
```

### 4. Cost Tracking

Track S3 storage growth over time:
- Poll `get_size_bytes()` every hour
- Store in time-series DB
- Calculate monthly cost estimate
- Alert if growth exceeds budget

## Next Steps

1. **Auto-Discovery Integration**: Automatically register discovered components for monitoring
2. **Alert Rules**: Define thresholds for metrics (e.g., "alert if CPU > 90%")
3. **Time-Series Storage**: Store metrics history for trend analysis
4. **Frontend Dashboard**: Visualize health and metrics in UI
5. **Custom Adapters**: Add adapters for Kubernetes, Kafka, Airflow, etc.
