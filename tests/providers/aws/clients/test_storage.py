import pytest
from moto import mock_aws
import boto3
from providers.aws.clients.storage import S3StorageClient


@mock_aws
def test_s3_create_bucket():
    """S3StorageClient creates buckets."""
    client = S3StorageClient(region="us-east-1")

    client.create_bucket("test-bucket")

    # Verify bucket exists
    s3 = boto3.client("s3", region_name="us-east-1")
    buckets = s3.list_buckets()["Buckets"]
    assert any(b["Name"] == "test-bucket" for b in buckets)


@mock_aws
def test_s3_upload_file(tmp_path):
    """S3StorageClient uploads files."""
    client = S3StorageClient(region="us-east-1")
    client.create_bucket("test-bucket")

    # Create test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world")

    client.upload_file(test_file, "test-bucket", "test.txt")

    # Verify file exists
    s3 = boto3.client("s3", region_name="us-east-1")
    obj = s3.get_object(Bucket="test-bucket", Key="test.txt")
    assert obj["Body"].read().decode() == "hello world"


@mock_aws
def test_s3_download_file(tmp_path):
    """S3StorageClient downloads files."""
    client = S3StorageClient(region="us-east-1")
    client.create_bucket("test-bucket")

    # Upload file
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world")
    client.upload_file(test_file, "test-bucket", "test.txt")

    # Download to new location
    download_path = tmp_path / "downloaded.txt"
    client.download_file("test-bucket", "test.txt", download_path)

    assert download_path.read_text() == "hello world"
