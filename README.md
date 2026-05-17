# NanoML

**Production ML Recommendation Systems Made Easy**

NanoML is a pip-installable framework that scaffolds complete end-to-end ML recommendation systems, enabling users to focus on ML business logic (features, models, labels) while the framework handles all infrastructure complexity.

## Features

- 🚀 **One-command deployment** - `nanoml deploy` handles everything
- ☁️ **Cloud-agnostic** - Same code runs on local/AWS/GCP/Azure
- 🔧 **Fully declarative** - Write WHAT, framework generates HOW
- 📦 **Complete stack** - 11 infrastructure services integrated
- 🎯 **Focus on ML** - Users customize ~15 files, framework handles 100+

## Quick Start

### Installation

```bash
pip3 install nanoml
```

### Create a New Project

```bash
nanoml init my-recommender
cd my-recommender
```

### Quick Start (No Docker Required)

```bash
# 1. Install framework and dashboard
make setup

# 2. Run example (shows placeholders)
make run

# 3. [Optional] Start visual dashboard
make dashboard    # Opens at http://localhost:3001

# 4. [Optional] See working demo with real results
make demo    # Fill skeleton with working code
make run     # Now shows actual ML pipeline results!
```

**By default**, the example shows skeleton code with placeholders. Use `make demo` to see it actually work!

### Cloud Deployment (Requires Docker)

When you're ready to deploy to production:

```bash
# Edit config.yaml: environment: aws|gcp|azure
nanoml deploy
```

Docker is used internally for cloud deployment but you never interact with it directly.

### [Optional] Test Production Stack Locally

Want to test with full infrastructure (Kafka, MLflow, Airflow) before deploying?

**Prerequisites:** Install [Docker](https://docs.docker.com/get-docker/) and Docker Compose.

```bash
make infra-up     # Start all 11 services locally
make infra-status # Check health
```

**Note:** This is completely optional. Most development happens without this.

### Run Model Training

```bash
# Run the full ML pipeline (data ingestion → training → serving)
python examples/movie_recommendations/pipeline.py
```

### Start Frontend Dashboard

```bash
# Easy way (after make setup)
make dashboard

# Or manually
cd infrastructure/dashboard
npm start
# Dashboard will be available at http://localhost:3001
```

The dashboard displays:
- **ML Pipeline DAG** - Visual flow of your pipeline stages (Raw Data → Data Processing → Feature Store → Model Training → Model Serving)
- **Infrastructure Services** - Quick links to MLflow, Airflow, Flink, and Lineage tracking

### Deploy to Cloud

```bash
# Edit config.yaml: environment: aws
nanoml deploy
```

## When Do You Need Docker?

### ✅ Local Development (No Docker)
- **Learning the framework** - `make setup && make run`
- **Writing ML code** - Pure Python development
- **Running examples** - Works out of the box
- **Model training** - PyTorch/scikit-learn runs locally
- **99% of development** - No infrastructure needed

### 🐳 Docker ONLY For:
- **Cloud deployment** - `nanoml deploy` (AWS/GCP/Azure)
- **[Optional] Testing production stack locally** - `make infra-up`

**TL;DR:** Docker is only required when deploying to cloud. Everything else runs locally without Docker.

**Important:** The same Python code runs both locally and in the cloud - no changes needed!

---

## Architecture

**11 Infrastructure Services (Optional - Docker):**
1. Storage (S3/GCS/Blob)
2. Message Queue (Kafka)
3. Stream Processing (Flink)
4. Feature Store (Feast)
5. Training (SageMaker/Vertex AI)
6. Experiment Tracking (MLflow)
7. Model Serving
8. API Gateway
9. Orchestration (Airflow)
10. Lineage Tracking
11. Frontend Dashboard

**Zero Duplication:** All infrastructure centralized, cloud providers in single files.

## What You Customize vs What's Provided

### Files You Implement (~15 files)

Users focus on ML business logic in these files:

| File | Purpose | What You Define |
|------|---------|-----------------|
| **Data Pipeline** |
| `data/loader.py` | Data ingestion | Where/how to load your dataset |
| `data/cleaner.py` | Data cleaning | Your cleaning rules and transformations |
| `data/labeling.py` | Label generation | How to create training labels |
| `data/splitter.py` | Train/test split | Your split strategy |
| **Features** |
| `features/definitions.py` | Feature definitions | Features to compute (declarative) |
| **Training** |
| `training/model.py` | Model architecture | Your neural network/model structure |
| `training/trainer.py` | Training logic | Hyperparameters, loss functions |
| `training/config.py` | Training config | Batch size, learning rate, etc. |
| **Evaluation** |
| `evaluation/metrics.py` | Metrics | Which metrics to track (accuracy, NDCG, etc.) |
| **Serving** |
| `serving/candidate_generation.py` | Candidate retrieval | Initial candidate pool logic |
| `serving/ranking.py` | Ranking | Re-ranking algorithm |
| `serving/postprocessing.py` | Post-processing | Deduplication, filtering rules |
| `serving/recommendation.py` | Final endpoint | Assemble recommendation response |
| **Config** |
| `config.yaml` | Project config | Project name, cloud provider, settings |

### Framework Auto-Generates (100+ files)

NanoML automatically generates from your definitions:

- **Flink Jobs** - Streaming feature computation from `features/definitions.py`
- **Feast Configs** - Feature store setup (feature_store.yaml, feature_definitions.py)
- **Airflow DAGs** - Orchestration workflows from your components
- **Infrastructure** - Docker Compose, K8s manifests, Terraform configs
- **API Gateway** - REST endpoints for serving recommendations
- **Monitoring** - MLflow experiments, lineage tracking

**You never write:**
- Flink job code
- Airflow DAG code
- Feast configuration
- Docker/K8s configs
- API server code
- Monitoring setup

## Documentation

- [Local Development Mode](LOCAL_MODE.md) - Run without Docker
- [Write Once, Run Anywhere](PORTABILITY.md) - Same code, local to cloud
- [Design Document](docs/superpowers/specs/2026-05-17-nanoml-design.md)
- [Implementation Plans](docs/superpowers/plans/)

## Development

### Install Development Dependencies

```bash
pip3 install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/ -v
pytest tests/ --cov=nanoml
```

### Code Quality

```bash
black nanoml/ tests/
ruff check nanoml/ tests/
```

## Architecture Principles

- **Fully declarative** - No custom Flink/Airflow code
- **Infrastructure-first** - 11 services in `infrastructure/`
- **Zero duplication** - One provider file per cloud
- **Three-layer** - User → Generated → Infrastructure

## License

MIT

## Links

- GitHub: https://github.com/nanoml/nanoml
- Documentation: https://nanoml.dev
- Issues: https://github.com/nanoml/nanoml/issues
