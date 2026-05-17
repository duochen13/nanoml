"""
Movie Recommendations Pipeline

Orchestrates all components:
1. Data ingestion
2. Feature computation
3. Model training
4. Model evaluation
5. Model serving
"""
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from components.data import DataComponent
from components.features import FeaturesComponent
from components.training import TrainingComponent
from components.evaluation import EvaluationComponent
from components.serving import ServingComponent


def main():
    """Run the full pipeline."""
    project_root = Path(__file__).parent

    print("=" * 60)
    print("NanoML Movie Recommendations Pipeline")
    print("=" * 60)

    # Step 1: Data ingestion
    print("\n[1/5] Data Ingestion")
    print("-" * 60)
    data = DataComponent(name="data_ingestion", schedule="@once")
    try:
        data.run(project_root / "data")
    except Exception as e:
        print(f"⚠ Data ingestion skipped: {e}")
        print("  (This requires infrastructure services running)")

    # Step 2: Feature computation
    print("\n[2/5] Feature Computation")
    print("-" * 60)
    features = FeaturesComponent(
        name="feature_computation",
        depends_on=[data],
        schedule="@daily"
    )
    features.run()

    # Step 3: Model training
    print("\n[3/5] Model Training")
    print("-" * 60)
    training = TrainingComponent(
        name="model_training",
        depends_on=[features],
        schedule="@daily"
    )
    training.run()

    # Step 4: Model evaluation
    print("\n[4/5] Model Evaluation")
    print("-" * 60)
    evaluation = EvaluationComponent(
        name="model_evaluation",
        depends_on=[training],
        schedule="@daily"
    )
    evaluation.run()

    # Step 5: Model serving
    print("\n[5/5] Model Serving")
    print("-" * 60)
    serving = ServingComponent(
        name="model_serving",
        depends_on=[evaluation],
        schedule="@once"
    )
    serving.run()

    print("\n" + "=" * 60)
    print("✨ Pipeline complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  - Start infrastructure: make infra-up")
    print("  - Model serving at: http://localhost:8000/recommendations")
    print("  - MLflow UI: http://localhost:5001")
    print("  - Airflow UI: http://localhost:8090")
    print("\nTry: curl 'http://localhost:8000/recommendations?user_id=1&top_k=5'")


if __name__ == "__main__":
    main()
