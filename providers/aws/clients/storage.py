import boto3
from pathlib import Path
from typing import Optional


class S3StorageClient:
    """Amazon S3 storage client.

    Implements same interface as local StorageClient but uses S3.
    """

    def __init__(self, region: str = "us-east-1"):
        """Initialize S3 client.

        Args:
            region: AWS region
        """
        self.region = region
        self.s3 = boto3.client("s3", region_name=region)

    def create_bucket(self, bucket_name: str):
        """Create S3 bucket.

        Args:
            bucket_name: Bucket name
        """
        if self.region == "us-east-1":
            # us-east-1 doesn't need LocationConstraint
            self.s3.create_bucket(Bucket=bucket_name)
        else:
            self.s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": self.region}
            )

    def upload_file(self, local_path: Path, bucket: str, key: str):
        """Upload file to S3.

        Args:
            local_path: Path to local file
            bucket: S3 bucket name
            key: S3 object key
        """
        self.s3.upload_file(str(local_path), bucket, key)

    def download_file(self, bucket: str, key: str, local_path: Path):
        """Download file from S3.

        Args:
            bucket: S3 bucket name
            key: S3 object key
            local_path: Path to save file
        """
        self.s3.download_file(bucket, key, str(local_path))

    def exists(self, bucket: str, key: str) -> bool:
        """Check if object exists in S3.

        Args:
            bucket: S3 bucket name
            key: S3 object key

        Returns:
            True if object exists
        """
        try:
            self.s3.head_object(Bucket=bucket, Key=key)
            return True
        except:
            return False

    def list_objects(self, bucket: str, prefix: str = "") -> list[str]:
        """List objects in S3 bucket.

        Args:
            bucket: S3 bucket name
            prefix: Key prefix to filter

        Returns:
            List of object keys
        """
        response = self.s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

        if "Contents" not in response:
            return []

        return [obj["Key"] for obj in response["Contents"]]
