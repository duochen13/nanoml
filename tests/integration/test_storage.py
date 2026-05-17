import pytest
from pathlib import Path
from infrastructure.storage.client import StorageClient
import socket


def _is_service_available(host: str, port: int) -> bool:
    """Check if service is available."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


@pytest.fixture
def storage_client():
    """Create storage client for testing."""
    return StorageClient(endpoint_url="http://localhost:4566")


def test_storage_client_connects(storage_client):
    """Storage client should connect to LocalStack."""
    if not _is_service_available("localhost", 4566):
        pytest.skip("LocalStack not running")

    buckets = storage_client.list_buckets()
    assert isinstance(buckets, list)


def test_storage_upload_download(storage_client, tmp_path):
    """Should upload and download files."""
    if not _is_service_available("localhost", 4566):
        pytest.skip("LocalStack not running")

    # Create test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello NanoML")

    # Upload
    bucket = "nanoml-test"
    key = "test/test.txt"
    storage_client.create_bucket(bucket)
    storage_client.upload_file(str(test_file), bucket, key)

    # Download
    download_path = tmp_path / "downloaded.txt"
    storage_client.download_file(bucket, key, str(download_path))

    assert download_path.read_text() == "Hello NanoML"
