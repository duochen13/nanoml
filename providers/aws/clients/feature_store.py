import boto3
from typing import Any


class SageMakerFeatureStoreClient:
    """Amazon SageMaker Feature Store client."""

    def __init__(self, region: str = "us-east-1"):
        """Initialize Feature Store client."""
        self.region = region
        self.sagemaker = boto3.client("sagemaker", region_name=region)
        self.runtime = boto3.client("sagemaker-featurestore-runtime", region_name=region)

    def create_feature_group(
        self,
        name: str,
        record_identifier: str,
        event_time_feature: str,
        features: list[str],
        s3_uri: str = None
    ) -> str:
        """Create SageMaker feature group.

        Args:
            name: Feature group name
            record_identifier: Record ID feature name
            event_time_feature: Timestamp feature name
            features: List of feature names
            s3_uri: S3 URI for offline store

        Returns:
            Feature group name
        """
        feature_definitions = [
            {"FeatureName": feat, "FeatureType": "String"}
            for feat in features
        ]

        # Add record identifier and event time
        feature_definitions.extend([
            {"FeatureName": record_identifier, "FeatureType": "String"},
            {"FeatureName": event_time_feature, "FeatureType": "String"}
        ])

        config = {
            "FeatureGroupName": name,
            "RecordIdentifierFeatureName": record_identifier,
            "EventTimeFeatureName": event_time_feature,
            "FeatureDefinitions": feature_definitions,
            "OnlineStoreConfig": {"EnableOnlineStore": True},
            "OfflineStoreConfig": {
                "S3StorageConfig": {"S3Uri": s3_uri or "s3://default-bucket/"}
            },
            "RoleArn": "arn:aws:iam::123456789012:role/SageMakerRole"
        }

        self.sagemaker.create_feature_group(**config)

        return name

    def put_record(self, feature_group_name: str, record: dict[str, Any]):
        """Write record to feature store.

        Args:
            feature_group_name: Feature group name
            record: Record data
        """
        # Convert record to Feature Store format
        features = [
            {"FeatureName": k, "ValueAsString": str(v)}
            for k, v in record.items()
        ]

        self.runtime.put_record(
            FeatureGroupName=feature_group_name,
            Record=features
        )

    def get_record(self, feature_group_name: str, record_id: str) -> dict:
        """Retrieve record from feature store.

        Args:
            feature_group_name: Feature group name
            record_id: Record identifier

        Returns:
            Record data
        """
        response = self.runtime.get_record(
            FeatureGroupName=feature_group_name,
            RecordIdentifierValueAsString=record_id
        )

        # Convert from Feature Store format
        record = {
            feat["FeatureName"]: feat["ValueAsString"]
            for feat in response["Record"]
        }

        return record
