"""Storage client wrapper for S3-compatible storage."""

import boto3
from typing import List, Optional
from pathlib import Path


class StorageClient:
    """Client for interacting with S3-compatible storage (LocalStack, AWS S3, etc.)."""

    def __init__(self, endpoint_url: Optional[str] = None, region: str = "us-east-1"):
        """
        Initialize storage client.

        Args:
            endpoint_url: S3 endpoint URL (e.g., "http://localhost:4566" for LocalStack)
            region: AWS region
        """
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            region_name=region,
            aws_access_key_id="test" if endpoint_url else None,
            aws_secret_access_key="test" if endpoint_url else None,
        )

    def list_buckets(self) -> List[str]:
        """List all S3 buckets."""
        response = self.client.list_buckets()
        return [bucket["Name"] for bucket in response.get("Buckets", [])]

    def create_bucket(self, bucket: str) -> None:
        """Create S3 bucket if it doesn't exist."""
        if bucket not in self.list_buckets():
            self.client.create_bucket(Bucket=bucket)

    def upload_file(self, file_path: str, bucket: str, key: str) -> None:
        """
        Upload file to S3.

        Args:
            file_path: Local file path
            bucket: S3 bucket name
            key: S3 object key
        """
        self.client.upload_file(file_path, bucket, key)

    def download_file(self, bucket: str, key: str, file_path: str) -> None:
        """
        Download file from S3.

        Args:
            bucket: S3 bucket name
            key: S3 object key
            file_path: Local destination path
        """
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        self.client.download_file(bucket, key, file_path)

    def delete_object(self, bucket: str, key: str) -> None:
        """Delete object from S3."""
        self.client.delete_object(Bucket=bucket, Key=key)

    def list_objects(self, bucket: str, prefix: str = "") -> List[str]:
        """List objects in bucket with optional prefix."""
        response = self.client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        return [obj["Key"] for obj in response.get("Contents", [])]
