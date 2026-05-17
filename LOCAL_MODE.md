# Local Development Mode (No Docker)

NanoML can run in **local mode** without any Docker infrastructure. This is perfect for:
- Learning the framework
- Developing features and models
- Quick prototyping
- Running examples

## Write Once, Run Anywhere

**The same Python code runs both locally and in the cloud - zero changes required.**

```python
# This code works everywhere - local, Docker, AWS, GCP, Azure
data.run(project_root / "data")
features.run()
training.run()
```

The framework automatically detects the environment and uses:
- **Local mode:** Filesystem, console logging, in-memory state
- **Cloud mode:** S3, Kafka, MLflow, distributed processing

You write business logic once, the framework handles the infrastructure.

## Quick Start

```bash
# 1. Install
make setup

# 2. Run
make run

# That's it! No Docker needed.
```

## What Runs Locally?

In local mode, the framework uses:

### ✅ Works Without Docker
- **Python code execution** - All your ML code
- **Data loading** - From local CSV/JSON files
- **Feature computation** - Pure Python transformations
- **Model training** - PyTorch/scikit-learn runs locally
- **Model evaluation** - Metrics computed locally
- **Predictions** - Models run in-process

### 📝 Simulated (No Real Infrastructure)
- **S3 storage** - Uses local filesystem instead
- **Kafka events** - Logged to console instead
- **MLflow tracking** - Skipped (or use SQLite backend)
- **Redis cache** - In-memory Python dict
- **Airflow orchestration** - Sequential execution

## Example: Movie Recommendations

The `examples/movie_recommendations/` example demonstrates local mode:

```bash
cd examples/movie_recommendations
python3 pipeline.py
```

**What happens:**
1. ✅ Downloads MovieLens dataset (no S3 needed)
2. ✅ Computes features (pure Python)
3. ✅ Trains model (PyTorch locally)
4. ✅ Evaluates model (local metrics)
5. ✅ Serves predictions (in-process)

**What's skipped:**
- ⏭️ Kafka event publishing (logged instead)
- ⏭️ MLflow tracking (or uses SQLite)
- ⏭️ S3 uploads (uses local files)

## When is Docker Used?

### Docker is ONLY Required For:

**1. Cloud Deployment**
```bash
nanoml deploy  # Deploys to AWS/GCP/Azure
```
Docker is used internally by the deployment process, but you don't interact with it.

### Docker is OPTIONAL For:

**2. Testing Production Stack Locally (Optional)**

Only add Docker if you want to test the full production infrastructure locally before deploying:

### 1. **Production-Like Testing**
Test your code with real Kafka, Redis, MLflow before deploying:
```bash
make infra-up  # Start all services
python3 pipeline.py  # Now uses real infrastructure
```

### 2. **Team Collaboration**
Share experiment results via MLflow UI:
```bash
make infra-up
# Access MLflow at http://localhost:5001
```

### 3. **Complex Workflows**
Orchestrate multi-step pipelines with Airflow:
```bash
make infra-up
# Access Airflow at http://localhost:8090
```

### 4. **Real-Time Features**
Process streaming data with Flink:
```bash
make infra-up
# Flink UI at http://localhost:9091
```

## Local Development Workflow

### Phase 1: Local Mode (Fast Iteration)
```bash
make setup
make run
# Edit code
make run
# Repeat...
```

### Phase 2: Add Infrastructure (When Ready)
```bash
make infra-up      # Start Docker services
python3 pipeline.py  # Now uses Kafka, MLflow, etc.
make infra-down    # Clean up when done
```

### Phase 3: Deploy to Cloud
```bash
nanoml deploy      # Deploy to AWS/GCP/Azure
```

## Benefits of Local Mode

### ⚡ Speed
- No Docker startup time (instant)
- No container overhead
- Faster iteration cycle

### 💻 Resource Efficient
- No 11 Docker containers running
- Lower memory usage (~100MB vs ~4GB)
- Laptop-friendly development

### 🔧 Simpler Debugging
- All code in same process
- Use your IDE debugger
- Print statements work
- No container logs to check

### 🚀 Lower Barrier to Entry
- No Docker installation required
- No Kubernetes knowledge needed
- Just Python skills

## Architecture Comparison

### Local Mode
```
┌─────────────────┐
│  Your Code      │
│  (Python)       │
│                 │
│  • Load CSV     │
│  • Train Model  │
│  • Predict      │
└─────────────────┘
```

### Full Infrastructure
```
┌─────────────────┐     ┌──────────────┐
│  Your Code      │────▶│ Kafka        │
│  (Python)       │     └──────────────┘
│                 │     ┌──────────────┐
│                 │────▶│ MLflow       │
│                 │     └──────────────┘
│                 │     ┌──────────────┐
│                 │────▶│ S3/LocalStack│
│                 │     └──────────────┘
│                 │     ┌──────────────┐
│                 │────▶│ Flink        │
└─────────────────┘     └──────────────┘
```

## Migration Path

Start local, add infrastructure as needed:

1. **Week 1:** Learn framework in local mode
2. **Week 2:** Add MLflow for experiment tracking
3. **Week 3:** Add Kafka for event processing
4. **Week 4:** Add Airflow for scheduling
5. **Production:** Deploy full stack to cloud

## Troubleshooting

### "ModuleNotFoundError" when running locally

Make sure you installed the framework:
```bash
make setup
# or
pip3 install -e ".[dev]"
```

### "Connection refused" errors

These are expected in local mode - the code gracefully handles missing services:
```python
try:
    kafka.send(event)
except Exception as e:
    print(f"⚠ Skipped: {e}")
    # Continue without Kafka
```

### Want to use some infrastructure but not all?

Start only specific services:
```bash
# Just MLflow
docker-compose -f deployment/docker-compose.yaml up mlflow -d

# MLflow + Redis
docker-compose -f deployment/docker-compose.yaml up mlflow redis -d
```

## Summary

**Local mode is the default and recommended way to start.**

You can build complete ML systems without ever touching Docker. Add infrastructure later when you need production features like distributed processing, centralized logging, or team collaboration.

```bash
# Start here
make setup
make run

# Add infrastructure when ready
make infra-up
```
