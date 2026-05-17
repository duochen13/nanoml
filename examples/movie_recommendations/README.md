# Movie Recommendations with NanoML

A complete end-to-end example demonstrating NanoML's capabilities using the MovieLens dataset.

## Overview

This example builds a movie recommendation system that:
- Ingests MovieLens data (100K ratings)
- Computes user and movie features using Flink
- Stores features in Feast
- Trains a recommendation model
- Evaluates model performance
- Serves recommendations via API

**Components:**
1. **Data**: Upload CSVs to S3, publish events to Kafka
2. **Features**: Flink streaming job → Feast feature store
3. **Training**: Fetch features, train Random Forest, log to MLflow
4. **Evaluation**: Evaluate model on test set
5. **Serving**: Deploy model, expose API endpoint

## Quick Start

### Prerequisites

- Python 3.9+
- NanoML installed (`pip install -e /path/to/nanoml`)
- (Optional) Docker and Docker Compose for infrastructure services

### Run the Example

```bash
# From this directory
./scripts/run_example.sh
```

This will:
1. Download MovieLens dataset (if not already downloaded)
2. Run the complete pipeline
3. Show next steps for infrastructure setup

## Manual Setup

### 1. Download Data

```bash
python3 data/download.py
```

This downloads ~100K movie ratings from MovieLens.

### 2. Run Pipeline

```bash
python3 pipeline.py
```

The pipeline orchestrates all 5 components in sequence.

## Project Structure

```
movie_recommendations/
├── nanoml.yaml               # Project config
├── data/
│   ├── download.py            # Dataset downloader
│   ├── movies.csv             # Movie metadata
│   └── ratings.csv            # User ratings
├── features/
│   └── definitions.py         # Feature group definitions
├── components/
│   ├── data.py                # Data ingestion
│   ├── features.py            # Feature computation
│   ├── training.py            # Model training
│   ├── evaluation.py          # Model evaluation
│   └── serving.py             # Model serving
├── pipeline.py                # Pipeline orchestration
├── scripts/
│   └── run_example.sh         # One-command setup
└── tests/
    └── test_*.py              # Unit and integration tests
```

## Feature Definitions

### User Features
- `total_ratings`: Number of movies rated
- `avg_rating`: Average rating given
- `rating_stddev`: Rating variance
- `favorite_genre`: Most watched genre

### Movie Features
- `genres`: Pipe-separated genres
- `release_year`: Extracted from title
- `avg_rating`: Average rating received
- `rating_count`: Number of ratings

### Interaction Features
- `last_rating_timestamp`: Most recent rating
- `days_since_last_rating`: Recency
- `rated_genres`: Genres user has rated

## Testing

Run all tests:
```bash
pytest tests/ -v
```

Run specific test modules:
```bash
pytest tests/test_dataset.py -v
pytest tests/test_data_component.py -v
pytest tests/test_end_to_end.py -v
```

## Infrastructure Setup (Optional)

To run with full infrastructure services:

### 1. Start Services

```bash
cd ../.. # Go to project root
make infra-up
```

This starts all 11 services:
- LocalStack (S3)
- Kafka
- Flink
- Feast
- MLflow
- Airflow
- Model Server
- API Gateway
- PostgreSQL
- Redis
- Grafana

### 2. Access Points

- **MLflow UI**: http://localhost:5001
  - View experiments, models, metrics

- **Airflow UI**: http://localhost:8080
  - View DAG structure and runs

- **Feast UI**: http://localhost:8888
  - Browse feature definitions

- **Model Server**: http://localhost:8000
  - API endpoint for recommendations

### 3. Run Pipeline with Infrastructure

With services running:
```bash
python3 pipeline.py
```

The data component will upload to S3 and publish to Kafka.

### 4. Get Recommendations

```bash
curl 'http://localhost:8000/recommendations?user_id=1&top_k=5'
```

## Implementation Notes

This example uses **simplified implementations** for demonstration:
- Components have placeholder logic
- Infrastructure connections use lazy initialization
- Tests focus on structure and API contracts

**For production use**, you would:
- Implement full Flink feature computation
- Train actual recommendation models (Matrix Factorization, Neural CF, etc.)
- Deploy to cloud infrastructure (AWS, GCP, Azure)
- Add monitoring and alerting
- Implement A/B testing

## Customization

### Change Features

Edit `features/definitions.py` and regenerate:

```bash
nanoml generate
```

### Change Model

Edit `components/training.py` to use a different algorithm.

### Change Schedule

Edit component `schedule` parameters in `pipeline.py`:

```python
training = TrainingComponent(
    name="model_training",
    schedule="@hourly"  # Instead of @daily
)
```

## Troubleshooting

### Dataset Download Fails

The dataset is downloaded from GroupLens. If the download fails:
- Check internet connection
- Try downloading manually from https://grouplens.org/datasets/movielens/

### Import Errors

Make sure you're running from the examples/movie_recommendations directory:
```bash
cd examples/movie_recommendations
python3 pipeline.py
```

### Infrastructure Services Not Running

Check service status:
```bash
cd ../.. && make infra-status
```

Start services if needed:
```bash
make infra-up
```

## Cleanup

Remove downloaded data:
```bash
rm -f data/movies.csv data/ratings.csv
```

Stop infrastructure (if running):
```bash
cd ../.. && make infra-down
```

## Next Steps

- Implement full feature computation with Flink
- Train production-grade recommendation models
- Deploy to AWS using `nanoml deploy --provider aws` (when available)
- Scale up with larger datasets (MovieLens 25M)
- Add real-time recommendation updates
- Implement A/B testing framework

## Learn More

- [NanoML Documentation](../../docs/)
- [Feature Engineering Guide](../../docs/superpowers/)
- [Component Development](../../docs/superpowers/)

## Dataset Attribution

This example uses the [MovieLens dataset](https://grouplens.org/datasets/movielens/):

> F. Maxwell Harper and Joseph A. Konstan. 2015. The MovieLens Datasets: History and Context.
> ACM Transactions on Interactive Intelligent Systems (TiiS) 5, 4: 19:1–19:19.
