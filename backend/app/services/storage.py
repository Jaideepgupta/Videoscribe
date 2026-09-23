"""
Object Storage Service (AWS S3 & MinIO abstraction).
"""

import io
import os
from typing import BinaryIO, Optional, Union
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from backend.app.config import settings


class StorageService:
    """Client wrapper for S3 and MinIO object storage operations."""

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        bucket_name: Optional[str] = None,
        region: Optional[str] = None,
    ):
        self.endpoint_url = endpoint_url or settings.S3_ENDPOINT_URL
        self.access_key = access_key or settings.S3_ACCESS_KEY_ID
        self.secret_key = secret_key or settings.S3_SECRET_ACCESS_KEY
        self.bucket_name = bucket_name or settings.S3_BUCKET_NAME
        self.region = region or settings.S3_REGION

        # Initialize boto3 client
        client_kwargs = {
            "service_name": "s3",
            "region_name": self.region,
            "aws_access_key_id": self.access_key,
            "aws_secret_access_key": self.secret_key,
            "config": Config(signature_version="s3v4", s3={"addressing_style": "path"}),
        }
        if self.endpoint_url:
            client_kwargs["endpoint_url"] = self.endpoint_url

        self.client = boto3.client(**client_kwargs)

    def ensure_bucket_exists(self) -> bool:
        """Verify if bucket exists, creating it if necessary."""
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError:
            try:
                self.client.create_bucket(Bucket=self.bucket_name)
                return True
            except Exception as e:
                # If cannot create (e.g. permission or offline), log and return False
                return False

    def upload_file(
        self,
        file_data: Union[bytes, BinaryIO, str],
        destination_key: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        Upload file bytes, stream, or local path to the target S3/MinIO key.
        Returns the destination key.
        """
        extra_args = {"ContentType": content_type}

        if isinstance(file_data, bytes):
            self.client.upload_fileobj(
                io.BytesIO(file_data),
                self.bucket_name,
                destination_key,
                ExtraArgs=extra_args,
            )
        elif isinstance(file_data, str) and os.path.isfile(file_data):
            self.client.upload_file(
                file_data,
                self.bucket_name,
                destination_key,
                ExtraArgs=extra_args,
            )
        elif hasattr(file_data, "read"):
            self.client.upload_fileobj(
                file_data,
                self.bucket_name,
                destination_key,
                ExtraArgs=extra_args,
            )
        else:
            raise ValueError("Unsupported file_data type. Expected bytes, stream, or valid file path.")

        return destination_key

    def download_file(self, destination_key: str, target_local_path: str) -> str:
        """Download remote object from S3/MinIO to local path."""
        os.makedirs(os.path.dirname(os.path.abspath(target_local_path)), exist_ok=True)
        self.client.download_file(self.bucket_name, destination_key, target_local_path)
        return target_local_path

    def generate_presigned_upload_url(
        self,
        destination_key: str,
        content_type: str = "video/mp4",
        expires_in: int = 3600,
    ) -> dict:
        """Generate presigned POST URL and fields for direct client-side upload."""
        try:
            response = self.client.generate_presigned_post(
                Bucket=self.bucket_name,
                Key=destination_key,
                Fields={"Content-Type": content_type},
                Conditions=[
                    {"Content-Type": content_type},
                    ["content-length-range", 1, settings.max_upload_size_bytes],
                ],
                ExpiresIn=expires_in,
            )
            return response
        except ClientError as e:
            raise RuntimeError(f"Failed to generate presigned upload URL: {e}")

    def generate_presigned_download_url(
        self,
        destination_key: str,
        expires_in: int = 3600,
    ) -> str:
        """Generate presigned GET URL for secure media download."""
        try:
            url = self.client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": self.bucket_name, "Key": destination_key},
                ExpiresIn=expires_in,
            )
            return url
        except ClientError as e:
            raise RuntimeError(f"Failed to generate presigned download URL: {e}")

    def delete_file(self, destination_key: str) -> bool:
        """Delete an object from bucket."""
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=destination_key)
            return True
        except ClientError:
            return False


storage_service = StorageService()
