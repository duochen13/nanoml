import csv
import json
import sys
from pathlib import Path
from typing import Optional

# Add infrastructure to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from infrastructure.storage.client import StorageClient
from infrastructure.kafka.client import KafkaClient


class DataComponent:
    """Ingests MovieLens data into NanoRec infrastructure.

    Responsibilities:
    1. Upload raw CSV files to S3 (LocalStack)
    2. Parse CSVs and publish events to Kafka
    3. Validate data format
    """

    def __init__(self, name: str, schedule: Optional[str] = None):
        """Initialize data component.

        Args:
            name: Component name
            schedule: Cron schedule (for Airflow)
        """
        self.name = name
        self.schedule = schedule or "@once"
        self._storage = None
        self._kafka = None

    @property
    def storage(self):
        """Lazy initialization of storage client."""
        if self._storage is None:
            self._storage = StorageClient(endpoint_url="http://localhost:4566")
        return self._storage

    @property
    def kafka(self):
        """Lazy initialization of Kafka client."""
        if self._kafka is None:
            self._kafka = KafkaClient()
        return self._kafka

    def run(self, data_dir: Path):
        """Run data ingestion.

        Args:
            data_dir: Directory containing movies.csv and ratings.csv
        """
        data_dir = Path(data_dir)

        # Validate inputs
        movies_file = data_dir / "movies.csv"
        ratings_file = data_dir / "ratings.csv"

        if not movies_file.exists() or not ratings_file.exists():
            raise FileNotFoundError("Missing movies.csv or ratings.csv")

        # Upload to S3
        self._upload_to_s3(movies_file, ratings_file)

        # Publish events to Kafka
        self._publish_movie_events(movies_file)
        self._publish_user_events(ratings_file)
        self._publish_rating_events(ratings_file)

        print(f"✓ Data ingestion complete")

    def _upload_to_s3(self, movies_file: Path, ratings_file: Path):
        """Upload CSV files to S3."""
        bucket = "nanorec-data"
        self.storage.create_bucket(bucket)

        self.storage.upload_file(str(movies_file), bucket, "movies.csv")
        self.storage.upload_file(str(ratings_file), bucket, "ratings.csv")

        print(f"✓ Uploaded to s3://{bucket}/")

    def _publish_movie_events(self, movies_file: Path):
        """Publish movie metadata events."""
        self.kafka.create_topic("movie_events")
        producer = self.kafka.create_producer()

        with open(movies_file) as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    event = {
                        "movie_id": int(row["movieId"]),
                        "title": row["title"],
                        "genres": row["genres"],
                        "timestamp": 0  # Static data, no real timestamp
                    }
                    producer.send("movie_events", value=event)
                except (KeyError, ValueError) as e:
                    raise ValueError(f"Invalid CSV format in movies.csv: {e}")

        producer.flush()
        producer.close()
        print(f"✓ Published movie events")

    def _publish_user_events(self, ratings_file: Path):
        """Publish user behavior events (aggregated from ratings)."""
        # Group by user
        user_stats = {}

        with open(ratings_file) as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    user_id = int(row["userId"])

                    if user_id not in user_stats:
                        user_stats[user_id] = {
                            "ratings": [],
                            "timestamps": []
                        }

                    user_stats[user_id]["ratings"].append(float(row["rating"]))
                    user_stats[user_id]["timestamps"].append(int(row["timestamp"]))

                except (KeyError, ValueError) as e:
                    raise ValueError(f"Invalid CSV format in ratings.csv: {e}")

        # Publish aggregated user events
        self.kafka.create_topic("user_events")
        producer = self.kafka.create_producer()

        for user_id, stats in user_stats.items():
            event = {
                "user_id": user_id,
                "total_ratings": len(stats["ratings"]),
                "avg_rating": sum(stats["ratings"]) / len(stats["ratings"]),
                "last_timestamp": max(stats["timestamps"]),
                "timestamp": max(stats["timestamps"])
            }
            producer.send("user_events", value=event)

        producer.flush()
        producer.close()
        print(f"✓ Published user events")

    def _publish_rating_events(self, ratings_file: Path):
        """Publish individual rating events."""
        self.kafka.create_topic("rating_events")
        producer = self.kafka.create_producer()

        with open(ratings_file) as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    event = {
                        "user_id": int(row["userId"]),
                        "movie_id": int(row["movieId"]),
                        "rating": float(row["rating"]),
                        "timestamp": int(row["timestamp"])
                    }
                    producer.send("rating_events", value=event)
                except (KeyError, ValueError) as e:
                    raise ValueError(f"Invalid CSV format in ratings.csv: {e}")

        producer.flush()
        producer.close()
        print(f"✓ Published rating events")
