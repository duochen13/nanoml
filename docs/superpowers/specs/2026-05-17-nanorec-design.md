# NanoRec - Production ML Recommendation Systems Made Easy

**Design Document**
**Date:** 2026-05-17
**Status:** Draft
**Author:** Design Session

---

## Executive Summary

**What:** NanoRec is a pip-installable framework that scaffolds complete end-to-end ML recommendation systems, enabling users to focus on ML business logic (features, models, labels) while the framework handles all infrastructure complexity.

**Why:** Building production ML systems requires integrating fragmented components (Kafka, Flink, Feast, SageMaker, Airflow, etc.). NanoRec demonstrates how these components connect and provides a template that works locally and deploys to any cloud (AWS/GCP/Azure) via a single config change.

**How:** Users `pip install nanorec`, run `nanorec init my-project`, customize 15 ML files, and deploy with one command. Same code runs everywhere.

**Architecture:** 11 total components:
- **9 CORE** (full implementation): Storage, Message Queue, Stream Processing, Feature Store, Training, Experiment Tracking, Model Serving, API Gateway, Orchestration
- **2 SHALLOW** (minimal viable implementation): Lineage Tracking, Frontend Dashboard

**Goal:** Integration demonstration over ML perfection. Users learn production ML architecture by using a working system.

---

## Table of Contents

1. [Project Goals](#project-goals)
2. [Installation & User Experience](#installation--user-experience)
3. [Architecture Overview](#architecture-overview)
4. [Component Design](#component-design)
   - [Implementation Levels](#implementation-levels)
5. [Data Flow & Integration](#data-flow--integration)
6. [Configuration & Deployment](#configuration--deployment)
7. [File Structure](#file-structure)
8. [Implementation Roadmap](#implementation-roadmap)

---

## 1. Project Goals

### Primary Goals

1. **Integration Demonstration** - Show how production ML components (Kafka, Flink, Feast, SageMaker, Airflow) connect
2. **User Focus** - Users customize only ML logic (~15 files), framework handles infrastructure (~100+ files)
3. **Cloud Agnostic** - Same code deploys to local/AWS/GCP/Azure via `config.yaml`
4. **Easy Onboarding** - `pip install nanorec` → `nanorec init` → working system in 5 minutes
5. **Educational** - Users learn production ML engineering by using the system

### Non-Goals

- Building SOTA recommendation models (focus is on integration, not model quality)
- Supporting every possible ML framework (start with PyTorch, expand later)
- Production-grade error handling (simplified for clarity)
- Cost optimization (users can optimize after understanding the system)
- **Custom low-level infrastructure code** - Users write high-level declarative business logic only. No custom Flink jobs, Airflow DAGs, or Feast materialization code. Framework generates all infrastructure code automatically.

### Success Criteria

✅ New user can go from zero to running system in < 5 minutes (local)
✅ User only edits ~15 ML files, framework handles rest
✅ Same code deploys to local/AWS/GCP/Azure via config change
✅ Clear integration points between all components
✅ LLM can navigate and modify the codebase easily

---

## 2. Installation & User Experience

### Installation Flow

```bash
# 1. Install NanoRec from PyPI
$ pip3 install nanorec

# 2. Create new project
$ nanorec init book-recommender
   Creating NanoRec project: book-recommender
   ✅ Project created!

# 3. Navigate to project
$ cd book-recommender

# 4. Customize ML files
$ vim data/loader.py          # Load dataset
$ vim features/definitions.py # Define features
$ vim training/model.py       # Build model
$ vim serving/recommendation.py # Recommendation logic

# 5. Deploy locally
$ make setup  # Install dependencies
$ make run    # Start Docker Compose services
   ✅ Local environment running!
   API: http://localhost:8000

# 6. Test
$ curl 'http://localhost:8000/recommend?user_id=123'
   {"recommendations": [...]}

# 7. Deploy to cloud
$ vim config.yaml  # Change environment: local → environment: aws
$ nanorec deploy
   ⚠️  Deploying to AWS (~$950/month)
   Continue? [y/N]: y
   [15 minutes later...]
   ✅ Deployed to AWS!
   API: https://abc123.execute-api.us-west-2.amazonaws.com/recommend
```

### CLI Commands

```bash
nanorec init <project-name>          # Create new project
nanorec init <name> --template <tmpl> # Use specific template
nanorec templates                     # List available templates
nanorec deploy                        # Deploy project
nanorec deploy --env aws              # Override environment
nanorec deploy --teardown             # Tear down infrastructure
nanorec validate                      # Validate config.yaml
nanorec test                          # Run smoke tests
nanorec --version                     # Show version
```

### User Journey

**Day 1: Local Development**
1. Install: `pip install nanorec`
2. Create: `nanorec init my-recommender`
3. Customize 15 ML files
4. Run: `make run`
5. Test: `curl localhost:8000/recommend?user_id=123`

**Day 7: Cloud Deployment**
1. Edit `config.yaml`: `environment: aws`
2. Deploy: `nanorec deploy`
3. Confirm: `y`
4. Wait 15 minutes
5. Test: `curl https://api.aws.../recommend?user_id=123`

---

## 3. Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER CUSTOMIZES (15 files)                   │
│  data/ | features/ | training/ | evaluation/ | serving/        │
└────────────────────┬────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│              NANOREC FRAMEWORK (100+ files)                     │
│  • Cloud-agnostic abstraction layer                             │
│  • Provider plugins (local/AWS/GCP/Azure)                       │
│  • Integration pipelines                                        │
│  • Deployment automation                                        │
└────────────────────┬────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│         INFRASTRUCTURE COMPONENTS                               │
│  Storage | Streaming | Features | Training | Serving |         │
│  Orchestration | Lineage | Dashboard                            │
└─────────────────────────────────────────────────────────────────┘
```

### System Architecture: Services vs Components

NanoRec has two distinct taxonomies:

**11 Infrastructure Services** (what gets deployed):
1. Storage, 2. Message Queue, 3. Stream Processing (Flink), 4. Feature Store (Feast), 5. Training (SageMaker), 6. Experiment Tracking (MLflow), 7. Model Serving, 8. API Gateway, 9. Orchestration (Airflow), 10. Lineage Tracking, 11. Frontend Dashboard

These live in `infrastructure/` and are deployed once, shared by all.

**9 Business Logic Components** (what users customize):
1. Data, 2. Features, 3. Training, 4. Evaluation, 5. Serving, 6. Orchestration, 7. Streaming, 8. Lineage, 9. Frontend

These live in component folders (`data/`, `features/`, etc.) and contain user files (✏️) + thin orchestration.

**Mapping:**

| Business Component | Uses Infrastructure Services |
|-------------------|----------------------------|
| Data | Storage |
| Features | Storage, Flink, Feast |
| Training | Feast, Storage, MLflow, SageMaker/Vertex/AzureML |
| Evaluation | Storage, Feast, MLflow, Model Server |
| Serving | Feast, Model Server, API Gateway |
| Orchestration | Airflow |
| Streaming | Message Queue (Kafka), Flink, Feast |
| Lineage | Lineage Tracking service |
| Frontend | Dashboard service |

**Note:** Some infrastructure services (Storage, Message Queue) have no corresponding user component because they're purely infrastructure - users don't customize them.

---

**Implementation Levels:**

- **CORE (9 services)**: Full cloud provider abstraction, production-ready
- **SHALLOW (2 services)**: Basic local-only implementation for learning

### Cloud Provider Support

**CORE Components (Full Cloud Support):**

| Component | Local | AWS | GCP | Azure |
|-----------|-------|-----|-----|-------|
| Storage | LocalStack | S3 | GCS | Blob Storage |
| Streaming (MQ) | Kafka | MSK | Pub/Sub | Event Hubs |
| Stream Processing | Flink | EMR/Kinesis | Dataflow | Stream Analytics |
| Feature Store | Feast (SQLite+Redis) | Feast (RDS+DynamoDB) | Feast (BigQuery+Firestore) | Feast (SQL+Cosmos) |
| Model Training | SageMaker local | SageMaker | Vertex AI | Azure ML |
| Experiment Tracking | MLflow (local) | MLflow (S3 backend) | MLflow (GCS backend) | MLflow (Blob backend) |
| Model Serving | Local server | SageMaker endpoint | Vertex AI endpoint | Azure ML endpoint |
| API Gateway | FastAPI | API Gateway+Lambda | Cloud Run | Azure Functions |
| Orchestration | Airflow (Docker) | MWAA | Cloud Composer | Data Factory |

**SHALLOW Components (Local Only):**

| Component | Local | AWS | GCP | Azure |
|-----------|-------|-----|-----|-------|
| Lineage Tracking | SQLite + FastAPI | _(not implemented)_ | _(not implemented)_ | _(not implemented)_ |
| Frontend Dashboard | React (local) | _(not implemented)_ | _(not implemented)_ | _(not implemented)_ |

---

## 4. Component Design

### Architecture: Infrastructure-First Design

NanoRec uses an **infrastructure-first** architecture to eliminate duplication and clarify ownership:

**The 11 Infrastructure Services (`infrastructure/`):**
- Storage, Kafka, Flink, Feast, SageMaker, MLflow, Model Server, API Gateway, Airflow, Lineage, Dashboard
- Each service deployed ONCE, used by ALL components
- Cloud providers centralized: `infrastructure/providers/{aws,gcp,azure}.py` (ONE file per cloud)

**Components (`data/`, `features/`, `training/`, etc.):**
- User files: ML business logic (✏️)
- Framework files: Thin orchestration that USES infrastructure services
- No component owns infrastructure - they import from `infrastructure/`

**Zero Duplication Guarantee:**
- AWS S3 logic: ONE place (`infrastructure/providers/aws.py`)
- Feast deployment: ONE place (`infrastructure/feast/`)
- Flink cluster: ONE place (`infrastructure/flink/`)

---

### Implementation Levels

NanoRec infrastructure services are implemented at two levels:

**CORE (9 services - Full Implementation):**
- Complete cloud provider abstraction (local/AWS/GCP/Azure)
- Production-quality error handling
- Full integration tests
- Comprehensive documentation
- Users rely on these for production workloads

**SHALLOW (2 services - Minimal Implementation):**
- Basic working implementation (local only)
- Demonstrates the concept and integration points
- Limited error handling
- "Good enough" for learning and development
- Users can enhance if needed, but not required for MVP

---

### 4.1 Data Component

**Purpose:** Load, clean, label, and split raw data

**User Files:**
- `data/loader.py` - Load dataset from Kaggle/S3/GCS
- `data/preprocessor.py` - Clean and transform data
- `data/labeling.py` - Generate labels for training
- `data/splitting.py` - Train/val/test split

**Framework Files:**
- `data/pipeline.py` - Orchestrates load → preprocess → label → split
  - Calls user's loader, preprocessor, labeling, splitting code
  - Uses `infrastructure/storage/client.py` to save results

**Uses Infrastructure Services:**
- `infrastructure/storage/` - Uploads train/val/test datasets to S3/GCS/Blob
- `infrastructure/providers/` - Cloud provider abstraction (selected by config.yaml)

**Integration Points:**
- Output: Writes train/val/test datasets to storage (S3/GCS/Blob)
- Next: Features component reads from storage

### 4.2 Features Component

**Purpose:** Define features, compute via Flink, store in Feast

**User Files (Declarative Business Logic):**
- `features/definitions.py` - Define features with `@feature` decorator
  - Transformations baked into definitions (eliminates train/serve skew)
  - Same transformed features stored in Feast for both training and serving
  - **Users write HIGH-LEVEL "what to compute", framework generates LOW-LEVEL "how to compute"**

**Framework Files:**
- `features/codegen.py` - Code generator that:
  - Reads user's `definitions.py`
  - Generates Flink jobs → `.nanorec/generated/flink/batch_features.py`
  - Generates Flink jobs → `.nanorec/generated/flink/stream_features.py`
  - Generates Feast configs → `.nanorec/generated/feast/feature_repo/features.py`

**Uses Infrastructure Services:**
- `infrastructure/flink/` - Submits generated jobs to Flink cluster
- `infrastructure/feast/` - Feature store (offline + online)
- `infrastructure/storage/` - Reads raw data from S3/GCS
- `infrastructure/providers/` - Cloud-specific implementations

**Declarative Feature Definition Example:**

```python
# USER WRITES (features/definitions.py):
from nanorec.features import feature

@feature(
    name="user_avg_rating",
    entity="user",
    input_columns=["user_id", "rating"],
    description="User's average rating across all books"
)
def compute_user_avg_rating(ratings_df):
    return ratings_df.groupby("user_id")["rating"].mean()

# FRAMEWORK GENERATES (.nanorec/generated/flink/batch_features.py):
def flink_batch_job():
    env = StreamExecutionEnvironment.get_execution_environment()
    ratings = env.read_csv("s3://data/ratings.csv")

    user_avg = ratings \
        .key_by(lambda x: x["user_id"]) \
        .aggregate(lambda ratings: sum(ratings) / len(ratings))

    write_to_feast_offline(user_avg, feature_name="user_avg_rating")

# FRAMEWORK GENERATES (.nanorec/generated/feast/feature_repo/features.py):
from feast import Feature, Entity, FeatureView

user_avg_rating_feature = Feature(
    name="user_avg_rating",
    dtype=Float32
)
```

**Key Design Decision: Store Transformed Features**

```
OLD (Problematic):
  Training: Raw features → offline_transforms.py → Model
  Serving: Raw features → online_transforms.py → Model
  Problem: Two transform files can diverge!

NEW (Correct):
  Flink: Raw data → [definitions.py] → TRANSFORMED features → Feast
  Training: Feast offline → Pre-transformed features → Model
  Serving: Feast online → Pre-transformed features → Model
  Solution: Single source of truth, zero skew!
```

**Integration Points:**
- Input: Reads data from `infrastructure/storage/`
- Output: Features in `infrastructure/feast/` (offline + online stores)
- Next: Training fetches from Feast offline, Serving fetches from Feast online

### 4.3 Training Component

**Purpose:** Train ML model using features from Feast

**User Files:**
- `training/model.py` - Model architecture (e.g., Neural Collaborative Filtering)
- `training/config.py` - Hyperparameters
- `training/trainer.py` - Custom training loop (optional, has default)

**Framework Files:**
- `training/pipeline.py` - Training pipeline orchestration
  1. Fetch features from Feast offline store (`feast.get_historical_features()`)
  2. Load train/val/test splits
  3. Call user's model
  4. Train with user's config
  5. Log to MLflow (metrics, params, artifacts)
  6. Save model to storage
- `training/callbacks.py` - Checkpointing, early stopping (optional)

**Uses Infrastructure Services:**
- `infrastructure/feast/` - Fetch offline features
- `infrastructure/storage/` - Load data splits, save trained model
- `infrastructure/mlflow/` - Experiment tracking
- `infrastructure/sagemaker/` - Submit training jobs (AWS/GCP/Azure)
- `infrastructure/providers/` - Cloud-specific training job submission

**Note:** Offline training only (no online learning in initial version)

**Integration Points:**
- Input: Features from `infrastructure/feast/` offline, data from `infrastructure/storage/`
- Output: Trained model saved to storage, logged in `infrastructure/mlflow/`
- Next: Serving component deploys model

### 4.4 Evaluation Component

**Purpose:** Evaluate model quality using offline metrics

**User Files:**
- `evaluation/metrics.py` - Define metrics (Precision@K, NDCG, AUC, F1, etc.)

**Framework Files:**
- `evaluation/evaluator.py` - Runs evaluation on test set
  - Loads model and test data
  - Computes all user-specified metrics
  - Logs results to MLflow

**Uses Infrastructure Services:**
- `infrastructure/storage/` - Load test data
- `infrastructure/feast/` - Fetch offline features
- `infrastructure/mlflow/` - Log evaluation metrics
- `infrastructure/model_server/` - Load trained model

**Integration Points:**
- Input: Model from storage, test data, features from `infrastructure/feast/`
- Output: Evaluation metrics logged to `infrastructure/mlflow/`

### 4.5 Serving Component

**Purpose:** Generate real-time recommendations via API

**User Files:**
- `serving/candidate_generation.py` - Generate candidate items to score (~100-1000 items)
- `serving/ranking.py` - Fetch features from Feast online, score with model, apply business rules
- `serving/postprocessing.py` - Apply diversity filters, business constraints
- `serving/recommendation.py` - Main recommendation pipeline (orchestrates above)

**Framework Files:**
- `serving/handler.py` - API request handler
  - Calls user's recommendation pipeline
  - Handles errors and logging

**Uses Infrastructure Services:**
- `infrastructure/api_gateway/` - HTTP API (FastAPI/Lambda/Cloud Run)
- `infrastructure/feast/` - Fetch online features
- `infrastructure/model_server/` - Model endpoint for scoring
- `infrastructure/providers/` - Cloud-specific API and model serving

**Simplified Error Handling:**
- Cold start: New user → show popular items (business logic)
- No complex fallbacks (circuit breakers, cached predictions removed for simplicity)

**Integration Points:**
- Input: User request → `infrastructure/feast/` online features → `infrastructure/model_server/`
- Output: JSON response with recommendations

### 4.6 Orchestration Component

**Purpose:** Orchestrate end-to-end pipeline with Airflow

**User Files (Declarative Configuration):**
- `orchestration/custom_operators.py` - Custom Airflow operators (optional, rare)
- **Most users don't write ANY orchestration code** - DAGs are auto-generated from their ML components

**Framework Files:**
- `orchestration/dag_factory.py` - Generates DAGs from user's ML components
  - Reads all component definitions (data, features, training, serving)
  - Creates DAGs in `.nanorec/generated/airflow/dags/`

**Generated DAGs (Automatic):**
- `.nanorec/generated/airflow/dags/data_pipeline.py` - Data loading orchestration
- `.nanorec/generated/airflow/dags/feature_pipeline.py` - Feature computation orchestration
- `.nanorec/generated/airflow/dags/training_pipeline.py` - Training orchestration
- `.nanorec/generated/airflow/dags/serving_pipeline.py` - Deployment orchestration

**Uses Infrastructure Services:**
- `infrastructure/airflow/` - Airflow server that executes generated DAGs
- `infrastructure/providers/` - Cloud-specific Airflow deployment (local/MWAA/Composer/Data Factory)

**Integration Points:**
- Orchestrates: All components via auto-generated DAGs
- Triggered: Scheduled (daily/weekly) or manual

### 4.7 Streaming Component

**Purpose:** Stream user events to Kafka for real-time feature updates

**User Files:**
- `streaming/event_schema.py` - Custom event schemas (optional, has defaults)

**Framework Files:**
- `streaming/event_generator.py` - Synthetic event generator (for demo)
- `streaming/producer.py` - Event producer wrapper

**Uses Infrastructure Services:**
- `infrastructure/kafka/` - Message queue (Kafka/MSK/Pub/Sub/Event Hubs)
- `infrastructure/flink/` - Runs streaming jobs that consume events
- `infrastructure/feast/` - Updates online features in real-time
- `infrastructure/providers/` - Cloud-specific message queue implementations

**Flow:** User events → `infrastructure/kafka/` → Flink stream job → `infrastructure/feast/` online store

**Integration Points:**
- Input: User events (real or synthetic)
- Output: Real-time feature updates in `infrastructure/feast/` online store

### 4.8 Lineage Tracking [SHALLOW]

**Implementation Level:** SHALLOW (Minimal viable implementation)

**Purpose:** Track ML artifact lineage and visualize DAG

**Location:** `infrastructure/lineage/` (Service #10)

**Implementation:**
- `infrastructure/lineage/tracker.py` - Basic tracking via `@track_lineage` decorator
  - Dataset versions (simple links)
  - Feature definitions (file hash)
  - Model training runs (basic metadata)
  - Deployments (timestamp + version)
- `infrastructure/lineage/metadata.db` - SQLite database (local only)
- `infrastructure/lineage/api.py` - Simple FastAPI endpoints

**Optional User Customization:**
- Users can import `@track_lineage` decorator to track custom artifacts (optional)

**Limitations (SHALLOW):**
- Local SQLite only (no cloud persistence)
- Basic metadata only (not production-grade)
- No advanced querying or search
- Minimal error handling

**Integration Points:**
- Auto-tracks: Basic component interactions
- Visualized: `infrastructure/dashboard/` (simple DAG view)

### 4.9 Frontend Dashboard [SHALLOW]

**Implementation Level:** SHALLOW (Minimal viable implementation)

**Purpose:** Visualize ML lineage DAG and pipeline status

**Location:** `infrastructure/dashboard/` (Service #11)

**Implementation:**
- `infrastructure/dashboard/src/` - React app (basic)
  - Simple lineage DAG: Dataset → Features → Model → Deployment
  - Basic pipeline status (running/completed/failed)
  - Simple metrics display (from `infrastructure/mlflow/`)
  - Basic component health check

**Limitations (SHALLOW):**
- Basic UI/UX (not polished)
- Limited interactivity
- No real-time updates (manual refresh)
- Local development only (no cloud deployment)

**User Interaction:**
- Works out-of-box for basic visualization
- Users CAN access `infrastructure/mlflow/` UI and `infrastructure/airflow/` UI directly for detailed views
- Optional: Users can enhance dashboard if desired (not required)

---

## 5. Data Flow & Integration

### 5.1 Training Pipeline (Offline)

```
STEP 1: DATA COMPONENT
───────────────────────────────────────────────────────────────
Kaggle/S3/GCS → [loader.py] → Raw Data
              → [preprocessor.py] → Cleaned Data
              → [labeling.py] → Labeled Data
              → [splitting.py] → Train/Val/Test

Output: train.parquet, val.parquet, test.parquet → Storage (S3/GCS)


STEP 2: FEATURES COMPONENT (Batch)
───────────────────────────────────────────────────────────────
Storage (S3/GCS) → Flink Batch Job
                 → Reads [definitions.py]
                 → Computes TRANSFORMED features
                 → Feast OFFLINE Store (SQLite/RDS/BigQuery)

Output: Features stored in Feast offline store


STEP 3: TRAINING COMPONENT
───────────────────────────────────────────────────────────────
Feast Offline Store → Get historical features (point-in-time correct)
Train/Val/Test Data → [model.py] → Model Architecture
                   → [trainer.py] → Training Loop
                   → SageMaker/Vertex/AzureML → Trained Model

MLflow → Track experiments (metrics, params, artifacts)
Lineage Tracker → Track dataset → features → model lineage

Output: Trained model → S3/GCS/Blob, logged in MLflow


STEP 4: EVALUATION COMPONENT
───────────────────────────────────────────────────────────────
Test Set + Feast Features → [metrics.py] → Evaluate Model

Output: Metrics logged to MLflow


STEP 5: DEPLOYMENT
───────────────────────────────────────────────────────────────
Model (S3/GCS) → Deploy to Serving Endpoint
               → SageMaker/Vertex/Azure ML endpoint

Output: Model serving endpoint ready
```

### 5.2 Serving Pipeline (Real-time)

```
STEP 1: API REQUEST
───────────────────────────────────────────────────────────────
User → API Gateway → /recommend?user_id=123


STEP 2: CANDIDATE GENERATION
───────────────────────────────────────────────────────────────
[candidate_generation.py] → Generate 100-1000 candidates

If no candidates (cold start):
  → Popular items fallback


STEP 3: FEATURE FETCHING
───────────────────────────────────────────────────────────────
Feast ONLINE Store (Redis/DynamoDB/Firestore)
  → Get features for user + candidate items
  → Features are PRE-TRANSFORMED (computed by Flink)
  → Fast access (< 10ms)


STEP 4: SCORING
───────────────────────────────────────────────────────────────
[ranking.py] → Call Model Endpoint (SageMaker/Vertex/Azure)
            → Score candidates
            → Apply business rules


STEP 5: POST-PROCESSING
───────────────────────────────────────────────────────────────
[postprocessing.py] → Apply diversity filters
                    → Business constraints


STEP 6: RESPONSE
───────────────────────────────────────────────────────────────
Return top-N recommendations as JSON
```

### 5.3 Streaming Pipeline (Continuous)

```
STEP 1: USER EVENTS
───────────────────────────────────────────────────────────────
User clicks/rates item → Event Producer → Kafka Topic


STEP 2: FLINK STREAMING
───────────────────────────────────────────────────────────────
Kafka → Flink Stream Job
     → Reads [definitions.py]
     → Computes TRANSFORMED features (same as batch)
     → Feast ONLINE Store (Redis/DynamoDB/Firestore)

Also: Append to Feast OFFLINE Store for future training


STEP 3: MATERIALIZATION (Periodic)
───────────────────────────────────────────────────────────────
Feast Offline → Materialization Job (every 15 minutes)
              → Feast Online

Ensures online store has latest batch-computed features
```

### 5.4 Feature Lifecycle (Offline vs Online)

```
┌─────────────────────────────────────────────────────────────────┐
│                     FEATURE LIFECYCLE                           │
└─────────────────────────────────────────────────────────────────┘

BATCH COMPUTATION (Daily/Hourly)
─────────────────────────────────
Raw Data (S3/GCS) → Flink Batch → OFFLINE Store
                     [definitions.py]   (RDS/BigQuery)
Timeline: Daily/Hourly
Storage: Large, historical (millions of rows)
Query: Slow (seconds to minutes)
Use: TRAINING

MATERIALIZATION (Every 15 min)
─────────────────────────────────
OFFLINE Store → Materialize → ONLINE Store
                               (Redis/DynamoDB)
Timeline: Every 1-15 minutes
Process: Copy latest features for active entities
Storage: Small, current (active users/items only)

STREAMING UPDATES (Real-time)
─────────────────────────────────
Events (Kafka) → Flink Stream → ONLINE Store (Redis/DynamoDB)
                 [definitions.py]    ↓
                                OFFLINE Store (append)
Timeline: Real-time (seconds)
Use: Fresh features for SERVING


WHEN EACH IS ACCESSED:
────────────────────────────────────────────────────────────────

TRAINING:  feast.get_historical_features() → OFFLINE Store
           (Point-in-time correct, historical data)

SERVING:   feast.get_online_features() → ONLINE Store
           (Latest values, fast < 10ms)

FALLBACK:  If ONLINE timeout → Try OFFLINE (slower 100-500ms)
```

### 5.5 Integration Validation (Smoke Tests)

**File: `integration/smoke_tests.py`**

Tests to validate all components connect correctly:

1. `test_data_to_storage()` - Data component writes to storage
2. `test_storage_to_features()` - Features component reads from storage
3. `test_features_to_feast()` - Flink writes features to Feast
4. `test_feast_to_training()` - Training fetches features from Feast
5. `test_training_to_model_registry()` - Trained model saved to S3/GCS
6. `test_model_to_serving()` - Model deployed to endpoint
7. `test_serving_to_feast_online()` - Serving fetches online features
8. `test_streaming_to_feast()` - Streaming updates Feast online
9. `test_end_to_end()` - Complete flow from data to serving

---

## 6. Configuration & Deployment

### 6.1 Configuration Structure

**Single file: `config.yaml`** (user edits this)

```yaml
# ENVIRONMENT SELECTION
environment: local  # Options: local, aws, gcp, azure

# PROJECT INFO
project:
  name: nanorec-book-recommender
  version: 1.0.0

# LOCAL ENVIRONMENT
local:
  storage:
    type: localstack
    endpoint: http://localhost:4566
  features:
    feast:
      offline_store:
        type: file
      online_store:
        type: redis
        host: localhost:6379
  training:
    sagemaker:
      mode: local
  serving:
    api:
      type: fastapi
      port: 8000

# AWS ENVIRONMENT
aws:
  region: us-west-2
  account_id: "123456789012"
  storage:
    type: s3
    bucket: nanorec-data-${account_id}
  features:
    feast:
      offline_store:
        type: redshift
      online_store:
        type: dynamodb
  training:
    sagemaker:
      instance_type: ml.m5.xlarge
  serving:
    api:
      type: api_gateway
    model:
      type: sagemaker_endpoint
      instance_type: ml.m5.xlarge

# GCP ENVIRONMENT
gcp:
  project_id: my-gcp-project
  region: us-central1
  storage:
    type: gcs
    bucket: nanorec-data
  features:
    feast:
      offline_store:
        type: bigquery
      online_store:
        type: firestore
  training:
    vertex_ai:
      machine_type: n1-standard-4
  serving:
    api:
      type: cloud_run

# AZURE ENVIRONMENT
azure:
  subscription_id: xxxxx
  resource_group: nanorec-rg
  storage:
    type: blob
    account_name: nanorecStorage
  features:
    feast:
      offline_store:
        type: azure_sql
      online_store:
        type: cosmosdb

# ML CONFIGURATION (Environment-agnostic)
ml:
  features:
    required_features:
      - user:user_avg_rating_normalized
      - user:user_total_books_log
      - item:item_popularity_score
  training:
    hyperparameters:
      embedding_dim: 64
      learning_rate: 0.001
      batch_size: 256
      epochs: 10
  serving:
    candidate_generation:
      max_candidates: 1000
    ranking:
      top_n: 10
```

### 6.2 One-Command Deployment

**Command: `nanorec deploy`**

**Flow:**
1. **Load configuration**
   - Parse `config.yaml`
   - Validate prerequisites (Docker running, cloud credentials, etc.)
   - Confirm cloud deployment (show cost estimate)

2. **Generate infrastructure code** (automatic, < 1 second)
   - `features/codegen.py` reads `features/definitions.py`
     → Generates `.nanorec/generated/flink/batch_features.py`
     → Generates `.nanorec/generated/flink/stream_features.py`
     → Generates `.nanorec/generated/feast/feature_repo/features.py`
   - `orchestration/dag_factory.py` reads all components
     → Generates `.nanorec/generated/airflow/dags/*.py`

3. **Deploy infrastructure** (one command)
   - **Local:** `docker-compose up -d` (all 11 services)
   - **AWS:** `terraform apply infrastructure/terraform/aws/`
   - **GCP:** `terraform apply infrastructure/terraform/gcp/`

4. **Submit generated jobs**
   - Submit Flink jobs to Flink cluster
   - Copy Airflow DAGs to Airflow server
   - Register Feast features with Feast server

5. **Run smoke tests**
   - Validate all 11 services are healthy
   - Test end-to-end data flow

6. **Report success**
   - Print endpoint URLs
   - Show next steps

**Time:**
- Local: ~2 minutes (Docker startup)
- AWS/GCP/Azure (first time): ~15 minutes (resource provisioning)
- AWS/GCP/Azure (updates): ~2-3 minutes (only changed resources)

**Key Insight:** Code generation is FAST (< 1 second). Users get one-command deployment with all the benefits of infrastructure-as-code.

### 6.3 Local Development (Docker Compose)

**File: `deployment/docker-compose.yaml`**

**11 Logical Services (9 CORE + 2 SHALLOW):**

Note: Some services require multiple Docker containers for proper operation.

**CORE Services (9 - Full Implementation):**
1. **Storage** - `localstack` (S3 emulation)
2. **Message Queue** - `kafka` + `zookeeper` (2 containers)
3. **Stream Processing** - `flink-jobmanager` + `flink-taskmanager` (2 containers)
4. **Feature Store** - `redis` (online) + `postgres` (offline) (2 containers)
5. **Experiment Tracking** - `mlflow`
6. **Model Serving** - `model-server`
7. **API Gateway** - `api` (FastAPI)
8. **Orchestration** - `airflow-webserver` + `airflow-scheduler` (2 containers)

**SHALLOW Services (2 - Minimal Implementation):**
9. **Lineage Tracking** - `lineage-api` (basic SQLite backend)
10. **Frontend Dashboard** - `dashboard` (basic React UI)

**Total: 11 logical services = 13 Docker containers**

**Commands:**
```bash
make run     # Start all 11 services
make clean   # Stop and remove all data
make test    # Run smoke tests
```

**Port Mapping:**
- API Gateway: http://localhost:8000
- Airflow UI: http://localhost:8080
- MLflow UI: http://localhost:5000
- Dashboard (SHALLOW): http://localhost:3000
- Lineage API (SHALLOW): http://localhost:9000

### 6.4 Cloud Deployment

**Provider Abstraction (Centralized):**

All cloud providers are centralized in `infrastructure/providers/`:
```
infrastructure/providers/
  base.py      # Abstract interfaces (StorageProvider, ComputeProvider, etc.)
  factory.py   # Selects provider based on config.yaml
  aws.py       # ALL AWS services (S3, SageMaker, MSK, EMR, etc.)
  gcp.py       # ALL GCP services (GCS, Vertex AI, Pub/Sub, etc.)
  azure.py     # ALL Azure services (Blob, Azure ML, Event Hubs, etc.)
```

**Factory Pattern:**

```python
# Component code (cloud-agnostic)
from infrastructure.providers import factory

storage = factory.create_storage()
storage.upload_file('local.txt', 's3://bucket/remote.txt')

# Framework selects provider based on config.yaml
# - local: Uses LocalStack
# - aws: Uses infrastructure/providers/aws.py → boto3 S3
# - gcp: Uses infrastructure/providers/gcp.py → GCS
# - azure: Uses infrastructure/providers/azure.py → Blob Storage
```

**Zero Duplication:** Each cloud provider has ONE implementation file, shared by ALL components.

**Migration Path:**

```
Day 1: Local Development
  config.yaml: environment: local
  All services: Docker Compose
  Cost: $0

Day 7: Cloud Deployment
  config.yaml: environment: aws
  Same ML code!
  Infrastructure auto-deployed
  Cost: ~$950/month

Later: Switch to GCP
  config.yaml: environment: gcp
  Same ML code!
  Cost: Similar
```

---

## 7. File Structure

### 7.1 NanoRec Package Structure (PyPI)

```
nanorec/                          # PyPI package
├── __init__.py
├── __version__.py
├── cli/                          # CLI commands
│   ├── main.py                   # Entry point
│   ├── init.py                   # Project scaffolding
│   ├── deploy.py                 # Deployment
│   └── validate.py               # Validation
├── templates/                    # Project templates
│   └── default/                  # Default template
│       ├── data/
│       ├── features/
│       ├── training/
│       ├── evaluation/
│       ├── serving/
│       ├── orchestration/
│       ├── streaming/
│       ├── tracking/
│       ├── frontend/
│       ├── core/
│       ├── integration/
│       ├── deployment/
│       └── config.yaml.template
├── core/                         # Shared framework code
│   ├── base.py
│   ├── registry.py
│   ├── factory.py
│   └── config_loader.py
└── setup.py                      # PyPI setup
```

### 7.2 Generated Project Structure (After `nanorec init`)

```
my-recommender/                   # User's project

# ============ GENERATED CODE (Auto-generated, gitignored) ============
.nanorec/
└── generated/                    # All generated artifacts (created by `nanorec deploy`)
    ├── flink/
    │   ├── batch_features.py     # Generated from features/definitions.py
    │   └── stream_features.py    # Generated from features/definitions.py
    ├── feast/
    │   └── feature_repo/         # Generated Feast feature definitions
    │       └── features.py
    └── airflow/
        └── dags/                 # Generated DAGs
            ├── data_pipeline.py
            ├── feature_pipeline.py
            └── training_pipeline.py

# ============ INFRASTRUCTURE (The 11 Services) ============
infrastructure/                   # CENTRALIZED - deployed once, used by all
                                  # SOURCE CODE ONLY (no generated files)
├── storage/                      # Service #1: S3/GCS/Blob
│   ├── client.py                 # Storage client wrapper
│   └── deployment/
│       ├── local.yaml            # LocalStack config
│       ├── aws.yaml              # S3 config
│       └── gcp.yaml              # GCS config
│
├── kafka/                        # Service #2: Message Queue
│   ├── client.py
│   └── deployment/
│
├── flink/                        # Service #3: Stream Processing
│   ├── client.py                 # Job submission client
│   └── deployment/               # Flink cluster config
│
├── feast/                        # Service #4: Feature Store
│   ├── client.py                 # Feast SDK wrapper
│   ├── materialization/          # Materialization scheduler
│   └── deployment/               # Feast server config
│       ├── feature_store.yaml.template
│       ├── local.yaml
│       └── aws.yaml
│
├── sagemaker/                    # Service #5: Training (SageMaker/Vertex/AzureML)
│   ├── client.py                 # Training job submission
│   └── deployment/               # Training environment config
│
├── mlflow/                       # Service #6: Experiment Tracking
│   ├── client.py                 # MLflow tracking client
│   └── deployment/               # MLflow server config
│
├── model_server/                 # Service #7: Model Serving
│   ├── client.py                 # Model endpoint client
│   └── deployment/               # Model server config
│
├── api_gateway/                  # Service #8: API Gateway
│   ├── app.py                    # FastAPI app entry point
│   └── deployment/               # API deployment config
│
├── airflow/                      # Service #9: Orchestration
│   ├── client.py                 # Airflow DAG submission
│   └── deployment/               # Airflow server config
│
├── lineage/                      # Service #10: Lineage Tracking (SHALLOW)
│   ├── tracker.py
│   ├── api.py
│   └── metadata.db               # SQLite (local only)
│
├── dashboard/                    # Service #11: Frontend (SHALLOW)
│   ├── src/                      # React app
│   └── deployment/
│
└── providers/                    # Cloud abstraction (NO DUPLICATION)
    ├── base.py                   # Abstract interfaces
    ├── factory.py                # Provider selection
    ├── aws.py                    # ALL AWS logic (S3, SageMaker, MSK, etc.)
    ├── gcp.py                    # ALL GCP logic (GCS, Vertex, Pub/Sub, etc.)
    └── azure.py                  # ALL Azure logic (Blob, AzureML, Event Hubs, etc.)

# ============ COMPONENTS (Use infrastructure) ============
data/
├── ✏️ loader.py                  # USER
├── ✏️ preprocessor.py            # USER
├── ✏️ labeling.py                # USER
├── ✏️ splitting.py               # USER
└── pipeline.py                   # FRAMEWORK: orchestrates user code
                                  #            uses infrastructure/storage

features/
├── ✏️ definitions.py             # USER
└── codegen.py                    # FRAMEWORK: generates Flink jobs
                                  #            → infrastructure/flink/jobs/
                                  #            → infrastructure/feast/feature_repo/

training/
├── ✏️ model.py                   # USER
├── ✏️ config.py                  # USER
├── ✏️ trainer.py                 # USER (optional)
└── pipeline.py                   # FRAMEWORK: training orchestration
                                  #            uses infrastructure/feast
                                  #            uses infrastructure/mlflow
                                  #            uses infrastructure/sagemaker

evaluation/
├── ✏️ metrics.py                 # USER
└── evaluator.py                  # FRAMEWORK: runs evaluation
                                  #            uses infrastructure/mlflow

serving/
├── ✏️ candidate_generation.py   # USER
├── ✏️ ranking.py                 # USER
├── ✏️ postprocessing.py          # USER
├── ✏️ recommendation.py          # USER
└── handler.py                    # FRAMEWORK: API request handler
                                  #            uses infrastructure/feast
                                  #            uses infrastructure/model_server

# ============ SHARED ============
core/                             # Framework utilities
├── base.py
├── registry.py
└── config_loader.py

integration/                      # Testing
├── end_to_end.py
└── smoke_tests.py

deployment/                       # Deployment configs
├── docker-compose.yaml           # All 11 services
├── Dockerfile.serving
└── terraform/

# ============ ROOT LEVEL ============
├── ✏️ config.yaml                # USER - MAIN CONFIG
├── Makefile
├── requirements.txt
└── README.md

# ============ SUMMARY ============
Layer 1 (User):           ~15 files (what users customize)
Layer 2 (Generated):      .nanorec/generated/ (auto-created, gitignored)
Layer 3 (Infrastructure): 11 services in infrastructure/
Cloud Providers:          3 files (aws.py, gcp.py, azure.py - ZERO duplication)

Total Docker containers:  13 (11 logical services, some need multiple containers)

# ============ VERSION CONTROL ============
.gitignore includes:
  - .nanorec/generated/      # All generated code (recreated on deploy)
  - .nanorec/cache/          # Downloaded datasets, model artifacts
  - infrastructure/*/data/   # Service data (Postgres, Redis, etc.)
```

### 7.3 File Organization Principles

**Three-Layer Architecture:**

**Layer 1: User Business Logic (What users write)**
- High-level declarative code: `features/definitions.py`, `training/model.py`, `serving/recommendation.py`
- Users write WHAT to compute, not HOW to run infrastructure
- Total: ~15 files across 9 components

**Layer 2: Generated Code (Auto-created by framework)**
- `.nanorec/generated/` - All generated artifacts (gitignored)
- Flink jobs, Feast feature definitions, Airflow DAGs
- Created automatically from Layer 1 during `nanorec deploy`
- Users never edit these files

**Layer 3: Infrastructure (Framework-provided)**
- `infrastructure/` - The 11 deployed services
- Source code only (no generated files mixed in)
- Services deployed ONCE and shared by all components
- Cloud providers centralized in `infrastructure/providers/` (ONE file per cloud)

**Data Flow:**
```
User writes:       features/definitions.py (declarative)
                          ↓
Framework generates: .nanorec/generated/flink/batch_features.py (imperative)
                          ↓
Framework deploys:   infrastructure/flink/ submits job to cluster
```

**Key Rules:**
1. **User business logic** → `<component>/*.py` (data, features, training, serving)
2. **Generated code** → `.nanorec/generated/` (never commit, auto-created)
3. **Infrastructure source** → `infrastructure/<service>/` (deployment configs + clients)
4. **Cloud providers** → `infrastructure/providers/{aws,gcp,azure}.py` (ONE file per cloud)

**Benefits:**
- **Fully declarative:** Users write high-level business logic only
- **No duplication:** AWS logic in ONE place, generated code in ONE place
- **Clear separation:** Source vs generated vs user code
- **One command:** `nanorec deploy` generates + deploys everything
- **LLM-friendly:** File location indicates its purpose and mutability

---

## 8. Implementation Roadmap

### Phase 1: Core Framework (MVP)

✅ Component architecture design
⏳ Core abstraction layer (base classes, factory, registry)
⏳ Local provider implementation (9 core components)
⏳ AWS provider implementation (9 core components)
⏳ Shallow implementation (2 components: Lineage + Dashboard)
⏳ CLI scaffolding (`nanorec init`, `nanorec deploy`)
⏳ Docker Compose local environment (all 11 services)
⏳ Basic smoke tests
⏳ Example project (book recommendations)

**Deliverable:** Working local → AWS deployment with all 11 components

### Phase 2: Additional Providers

⏳ GCP provider (9 core components)
⏳ Azure provider (9 core components)
⏳ Provider testing framework
⏳ Cross-cloud smoke tests

**Deliverable:** Support for AWS, GCP, Azure

### Phase 3: Developer Experience

⏳ Enhanced CLI (`nanorec validate`, `nanorec test`)
⏳ Interactive setup wizard
⏳ Pre-built model templates
⏳ Documentation (user guide, API reference)
⏳ Example projects (collaborative filtering, content-based)

**Deliverable:** Polished developer experience

### Phase 4: Advanced Features (Post-MVP)

⏳ Online training (optional module)
⏳ A/B testing framework
⏳ Model monitoring
⏳ Cost optimization tools
⏳ VS Code extension
⏳ Enhanced lineage tracking (cloud providers)
⏳ Enhanced dashboard (cloud deployment, real-time updates)

**Deliverable:** Production-ready advanced features

---

## Appendix A: Key Design Decisions

### Decision 1: Store Transformed Features in Feast
**Problem:** Training/serving skew (separate offline/online transform files)
**Solution:** Single source of truth - transformations in `features/definitions.py`
**Benefit:** Zero skew risk, simpler user code

### Decision 2: Offline Training Only
**Rationale:** Focus on integration, not ML complexity
**Benefit:** Clearer learning path, faster implementation
**Future:** Online learning can be added as optional module

### Decision 3: Simplified Error Handling
**Removed:** Circuit breakers, feature store fallbacks, complex retry logic
**Kept:** Cold start handling, basic Airflow retries
**Benefit:** Easier to understand, focus on happy path

### Decision 4: Top-Down Component Structure
**Pattern:** User files at top level, infrastructure in subdirectories
**Benefit:** Immediately clear what to customize, better for LLM navigation

### Decision 5: Config-Driven Multi-Cloud
**Approach:** Single `config.yaml` controls everything
**Benefit:** Minimize vendor lock-in, maximize portability

---

## Appendix B: Success Metrics

### User Onboarding
- ✅ Time to first working system: < 5 minutes
- ✅ Time to cloud deployment: < 20 minutes
- ✅ User satisfaction: 4.5/5 stars

### Code Quality
- ✅ Test coverage: > 80%
- ✅ LLM navigation success rate: > 90%
- ✅ User customization files: < 20

### Educational Impact
- ✅ Users understand production ML architecture
- ✅ Users can explain component integration
- ✅ Users can extend/modify the system

---

**End of Design Document**
