# NanoRec Infrastructure Services

This directory contains the 11 infrastructure services that power NanoRec.

## Services

### CORE (9 services - Full Implementation)

1. **Storage** (`storage/`) - LocalStack S3 for local, AWS S3 for cloud
2. **Message Queue** (`kafka/`) - Kafka for event streaming
3. **Stream Processing** (`flink/`) - Apache Flink for batch + streaming
4. **Feature Store** (`feast/`) - Feast with Redis (online) + Postgres (offline)
5. **Training** (`sagemaker/`) - SageMaker local mode / SageMaker / Vertex AI
6. **Experiment Tracking** (`mlflow/`) - MLflow tracking server
7. **Model Serving** (`model_server/`) - FastAPI model endpoint
8. **API Gateway** (`api_gateway/`) - FastAPI gateway
9. **Orchestration** (`airflow/`) - Apache Airflow

### SHALLOW (2 services - Minimal Implementation)

10. **Lineage Tracking** (`lineage/`) - Basic SQLite + FastAPI
11. **Frontend Dashboard** (`dashboard/`) - Basic React UI

## Quick Start

```bash
# Start all services
make infra-up

# Check service health
make infra-status

# Run integration tests
make infra-test

# Stop all services
make infra-down
```

## Service URLs (Local)

- API Gateway: http://localhost:8000
- MLflow UI: http://localhost:5000
- Airflow UI: http://localhost:8080
- Flink UI: http://localhost:8081
- Dashboard: http://localhost:3000
- Lineage API: http://localhost:9000

## Architecture

Each service has:
- `client.py` - Python client wrapper
- `deployment/` - Deployment configs (Dockerfile, init scripts)

The `deployment/docker-compose.yaml` orchestrates all services with proper networking and volume mounts.

## Adding a New Service

1. Create `infrastructure/<service>/client.py`
2. Create `infrastructure/<service>/deployment/`
3. Add service to `deployment/docker-compose.yaml`
4. Add health check to `core/health.py`
5. Add tests to `tests/integration/`
