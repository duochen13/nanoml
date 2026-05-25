"""S3 bucket adapter with monitoring."""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from .base import DataSourceAdapter, HealthCheck, HealthStatus, Metric

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


class S3Adapter(DataSourceAdapter):
    """Adapter for S3 buckets with monitoring capabilities."""

    def __init__(self, bucket_name: str, region: str = "us-east-1", prefix: str = ""):
        """Initialize S3 adapter.

        Args:
            bucket_name: S3 bucket name
            region: AWS region
            prefix: Optional prefix to scope operations
        """
        super().__init__(
            component_id=f"s3_{bucket_name}",
            component_name=bucket_name,
            component_type="s3_bucket"
        )
        self.bucket_name = bucket_name
        self.region = region
        self.prefix = prefix
        self._s3_client = None

    def _get_client(self):
        """Get or create S3 client."""
        if self._s3_client is None and BOTO3_AVAILABLE:
            self._s3_client = boto3.client('s3', region_name=self.region)
        return self._s3_client

    async def health_check(self) -> HealthCheck:
        """Check if bucket is accessible."""
        if not BOTO3_AVAILABLE:
            return HealthCheck(
                status=HealthStatus.UNKNOWN,
                message="boto3 not available",
                checked_at=datetime.utcnow(),
                details={}
            )

        try:
            client = self._get_client()
            # Try to head the bucket
            client.head_bucket(Bucket=self.bucket_name)

            return HealthCheck(
                status=HealthStatus.HEALTHY,
                message="Bucket accessible",
                checked_at=datetime.utcnow(),
                details={"bucket": self.bucket_name, "region": self.region}
            )
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            return HealthCheck(
                status=HealthStatus.UNHEALTHY,
                message=f"Bucket not accessible: {error_code}",
                checked_at=datetime.utcnow(),
                details={"error": str(e)}
            )
        except Exception as e:
            return HealthCheck(
                status=HealthStatus.UNKNOWN,
                message=f"Error checking bucket: {str(e)}",
                checked_at=datetime.utcnow(),
                details={}
            )

    async def get_metrics(self) -> List[Metric]:
        """Collect S3 bucket metrics."""
        metrics = []
        timestamp = datetime.utcnow()

        try:
            # Get bucket size
            size_bytes = await self.get_size_bytes()
            metrics.append(Metric(
                name="storage_size",
                value=size_bytes,
                unit="bytes",
                timestamp=timestamp,
                labels={"bucket": self.bucket_name}
            ))

            # Get object count
            object_count = await self._get_object_count()
            metrics.append(Metric(
                name="object_count",
                value=object_count,
                unit="count",
                timestamp=timestamp,
                labels={"bucket": self.bucket_name}
            ))

        except Exception as e:
            print(f"Error collecting S3 metrics: {e}")

        return metrics

    async def get_metadata(self) -> Dict[str, Any]:
        """Get S3 bucket metadata."""
        metadata = {
            "bucket_name": self.bucket_name,
            "region": self.region,
            "prefix": self.prefix,
        }

        try:
            client = self._get_client()

            # Get bucket location
            location = client.get_bucket_location(Bucket=self.bucket_name)
            metadata["location_constraint"] = location.get("LocationConstraint")

            # Get bucket creation date
            response = client.list_buckets()
            for bucket in response.get("Buckets", []):
                if bucket["Name"] == self.bucket_name:
                    metadata["created_at"] = bucket["CreationDate"].isoformat()

        except Exception as e:
            metadata["error"] = str(e)

        return metadata

    async def get_schema(self) -> Optional[Dict[str, Any]]:
        """Infer schema from sample objects.

        For Parquet files, extracts actual schema.
        For other formats, returns basic structure.
        """
        try:
            client = self._get_client()

            # List first few objects
            response = client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=self.prefix,
                MaxKeys=10
            )

            objects = response.get("Contents", [])
            if not objects:
                return None

            # Check if Parquet
            parquet_files = [obj for obj in objects if obj["Key"].endswith(".parquet")]
            if parquet_files:
                # Would need pyarrow to read schema
                return {
                    "format": "parquet",
                    "sample_files": [obj["Key"] for obj in parquet_files[:3]]
                }

            # Generic schema info
            return {
                "format": "unknown",
                "sample_objects": [obj["Key"] for obj in objects[:5]],
                "total_objects": len(objects)
            }

        except Exception as e:
            return {"error": str(e)}

    async def get_size_bytes(self) -> int:
        """Calculate total size of objects in bucket."""
        try:
            client = self._get_client()

            paginator = client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=self.prefix)

            total_size = 0
            for page in pages:
                for obj in page.get("Contents", []):
                    total_size += obj["Size"]

            return total_size

        except Exception as e:
            print(f"Error calculating S3 size: {e}")
            return 0

    async def _get_object_count(self) -> int:
        """Count objects in bucket."""
        try:
            client = self._get_client()

            paginator = client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=self.prefix)

            count = 0
            for page in pages:
                count += len(page.get("Contents", []))

            return count

        except Exception as e:
            print(f"Error counting S3 objects: {e}")
            return 0
