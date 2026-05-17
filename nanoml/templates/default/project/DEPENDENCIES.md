# Project Dependencies

This file explains what dependencies are installed and why.

## Core Dependencies

### NanoML Framework
- `nanoml>=0.1.0` - The framework itself

### Data Processing
- `pandas>=2.0.0` - DataFrames for data manipulation
- `numpy>=1.24.0` - Numerical operations
- `pyarrow>=12.0.0` - Efficient data serialization (used by Feast)

### ML Frameworks
- `torch>=2.0.0` - PyTorch for deep learning models
- `scikit-learn>=1.3.0` - Traditional ML algorithms

### Feature Store
- `feast>=0.35.0` - Feature store client (connects to Feast server in Docker)

### Experiment Tracking
- `mlflow>=2.8.0` - Experiment tracking client (connects to MLflow server in Docker)

### API Serving
- `fastapi>=0.104.0` - Web framework for serving APIs
- `uvicorn>=0.24.0` - ASGI server for FastAPI

### Infrastructure Clients
- `boto3>=1.28.0` - AWS S3 client (connects to LocalStack in Docker)
- `kafka-python>=2.0.0` - Kafka producer/consumer (connects to Kafka in Docker)

## What's NOT Included (Runs in Docker Instead)

These services run in Docker containers and don't need Python packages:

- ❌ **Apache Flink** - Stream processing runs in Docker (`flink:1.18` image)
- ❌ **Apache Airflow** - Orchestration runs in Docker (`apache/airflow` image)
- ❌ **Redis** - Cache runs in Docker (`redis:7` image)
- ❌ **PostgreSQL** - Database runs in Docker (`postgres:16` image)
- ❌ **Zookeeper/Kafka** - Message queue runs in Docker
- ❌ **LocalStack** - S3 emulation runs in Docker

## Why No Apache Flink Python Package?

The `apache-flink` Python package causes dependency conflicts with `apache-beam` and other packages.

**You don't need it because:**
1. NanoML generates Flink jobs from your feature definitions
2. Flink runs in a Docker container, not in your Python environment
3. The generated Flink code is deployed to the Docker container

## Installation

```bash
# Install all dependencies
pip3 install -r requirements.txt

# Or use make
make setup
```

## Troubleshooting

### Dependency Conflicts

If you encounter dependency conflicts:

```bash
# Use pip-tools to resolve conflicts
pip3 install pip-tools
pip-compile requirements.txt
pip3 install -r requirements.txt
```

### Platform-Specific Issues

Some packages (like `torch`) have platform-specific builds:

```bash
# macOS Apple Silicon
pip3 install torch --extra-index-url https://download.pytorch.org/whl/cpu

# CUDA GPU support
pip3 install torch --extra-index-url https://download.pytorch.org/whl/cu118
```

### Optional Dependencies

If you don't need certain features, you can comment them out:

```python
# requirements.txt
# torch>=2.0.0  # Comment out if not using PyTorch models
```

## Docker vs Python Packages

| Component | Python Package? | Why |
|-----------|----------------|-----|
| Your ML code | ✅ Yes | You write Python code |
| Feast client | ✅ Yes | To query features from Python |
| MLflow client | ✅ Yes | To log experiments from Python |
| Kafka client | ✅ Yes | To publish events from Python |
| Flink engine | ❌ No (Docker) | Generated jobs run in container |
| Airflow engine | ❌ No (Docker) | DAGs run in container |
| Redis | ❌ No (Docker) | Pure data store |
| PostgreSQL | ❌ No (Docker) | Pure database |
