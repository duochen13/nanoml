#!/bin/bash
set -e

echo "Setting up NanoML Movie Recommendations example..."

# Check if we're in the right directory
if [ ! -f "nanoml.yaml" ]; then
    echo "Error: Must run from examples/movie_recommendations directory"
    exit 1
fi

# Download data if not present
if [ ! -f "data/movies.csv" ] || [ ! -f "data/ratings.csv" ]; then
    echo "Downloading MovieLens dataset..."
    python3 data/download.py
fi

# Run pipeline
echo "Running pipeline..."
python3 pipeline.py

echo ""
echo "✅ Example complete!"
echo ""
echo "To start infrastructure services:"
echo "  cd ../.. && make infra-up"
echo ""
echo "Access points (when infrastructure is running):"
echo "  - Recommendations API: http://localhost:8000/recommendations"
echo "  - MLflow: http://localhost:5000"
echo "  - Airflow: http://localhost:8080"
echo "  - Feast UI: http://localhost:8888"
echo ""
echo "Try:"
echo "  curl 'http://localhost:8000/recommendations?user_id=1&top_k=10'"
