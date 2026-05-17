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
pip install nanoml
```

### Create a New Project

```bash
nanoml init my-recommender
cd my-recommender
```

### Local Development

```bash
make setup  # Install dependencies
make run    # Start Docker Compose (11 services)
```

### Run Model Training

```bash
# Run the full ML pipeline (data ingestion → training → serving)
python examples/movie_recommendations/pipeline.py
```

### Start Frontend Dashboard

```bash
# Install dependencies and start React dashboard
cd infrastructure/dashboard
npm install
npm start
# Dashboard will be available at http://localhost:3000
```

### Deploy to Cloud

```bash
# Edit config.yaml: environment: aws
nanoml deploy
```

## Architecture

**11 Infrastructure Services:**
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

## What You Customize

- `data/*.py` - Load, clean, label, split data
- `features/definitions.py` - Define features (declarative)
- `training/*.py` - Model architecture & config
- `serving/*.py` - Recommendation logic

**Framework auto-generates:**
- Flink jobs from feature definitions
- Airflow DAGs from components
- Feast configs
- Infrastructure deployment

## Documentation

- [Design Document](docs/superpowers/specs/2026-05-17-nanoml-design.md)
- [Implementation Plans](docs/superpowers/plans/)

## Development

### Install Development Dependencies

```bash
pip install -e ".[dev]"
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
