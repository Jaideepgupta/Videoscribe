"""
Unit tests for StorageService operations with mocked boto3 client.
"""

from unittest.mock import MagicMock, patch
import pytest
from backend.app.services.storage import StorageService


@pytest.fixture
def mock_storage():
    """Create StorageService with mocked boto3 S3 client."""
    with patch("boto3.client") as mock_boto:
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3
        service = StorageService(
            endpoint_url="http://mock-minio:9000",
            access_key="test_key",
            secret_key="test_secret",
            bucket_name="test-bucket",
            region="us-east-1",
        )
        service.client = mock_s3
        yield service, mock_s3


def test_upload_bytes(mock_storage):
    """Verify upload_file with raw bytes."""
    service, mock_s3 = mock_storage
    data = b"Sample video content payload"
    destination = "temp-media/test.mp4"

    res = service.upload_file(data, destination, content_type="video/mp4")
    assert res == destination
    mock_s3.upload_fileobj.assert_called_once()


def test_presigned_upload_url(mock_storage):
    """Verify presigned upload URL generation."""
    service, mock_s3 = mock_storage
    mock_s3.generate_presigned_post.return_value = {
        "url": "http://mock-minio:9000/test-bucket",
        "fields": {"key": "uploads/user123/video.mp4"},
    }

    result = service.generate_presigned_upload_url("uploads/user123/video.mp4")
    assert result["url"] == "http://mock-minio:9000/test-bucket"
    assert result["fields"]["key"] == "uploads/user123/video.mp4"
    mock_s3.generate_presigned_post.assert_called_once()


def test_presigned_download_url(mock_storage):
    """Verify presigned download URL generation."""
    service, mock_s3 = mock_storage
    mock_s3.generate_presigned_url.return_value = "https://mock-minio:9000/test-bucket/file.mp3?token=xyz"

    url = service.generate_presigned_download_url("audio/file.mp3")
    assert url == "https://mock-minio:9000/test-bucket/file.mp3?token=xyz"
    mock_s3.generate_presigned_url.assert_called_once()


def test_delete_file(mock_storage):
    """Verify file deletion calls S3 delete_object."""
    service, mock_s3 = mock_storage
    success = service.delete_file("temp/sample.mp4")
    assert success is True
    mock_s3.delete_object.assert_called_once_with(Bucket="test-bucket", Key="temp/sample.mp4")
