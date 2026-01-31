"""
AWS S3 Storage Client

This module provides utilities for interacting with AWS S3
using boto3.

Features:
    - Upload files to AWS S3
    - Delete files from AWS S3
    - Generate presigned URLs for file access
    - List files in bucket
"""

import os
import logging
import boto3
from botocore.exceptions import ClientError
from typing import Optional, BinaryIO
from datetime import datetime

logger = logging.getLogger(__name__)


class S3StorageClient:
    """AWS S3 Storage client using boto3."""

    def __init__(self):
        """Initialize AWS S3 client with credentials from environment."""
        self.access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.region = os.getenv("AWS_REGION", "ap-northeast-2")
        self.bucket_name = os.getenv("AWS_BUCKET_NAME")
        self.default_folder = os.getenv("AWS_STORAGE_FOLDER", "wedding-images")

        if not all([self.access_key, self.secret_key, self.bucket_name]):
            raise ValueError("AWS credentials are not properly configured in environment variables")

        # Create S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        )

        logger.info(f"✅ AWS S3 client initialized (bucket: {self.bucket_name}, folder: {self.default_folder})")

    def upload_file(
        self,
        file_data: BinaryIO,
        filename: str,
        content_type: Optional[str] = None,
        folder: str = None
    ) -> str:
        """
        Upload a file to AWS S3.

        Args:
            file_data: Binary file data
            filename: Original filename
            content_type: MIME type of the file
            folder: Folder path in bucket (default: uses AWS_STORAGE_FOLDER from env)

        Returns:
            str: File path in storage (key)

        Raises:
            ClientError: If upload fails
        """
        try:
            # Use default folder if not specified
            if folder is None:
                folder = self.default_folder

            # Generate unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = os.path.splitext(filename)[1]
            unique_filename = f"{timestamp}_{filename}"
            file_path = f"{folder}/{unique_filename}"

            # Upload configuration
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type

            # Upload to S3
            self.s3_client.upload_fileobj(
                file_data,
                self.bucket_name,
                file_path,
                ExtraArgs=extra_args
            )

            logger.info(f"✅ File uploaded: {file_path}")
            return file_path

        except ClientError as e:
            logger.error(f"❌ Upload failed: {e}")
            raise e

    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from AWS S3.

        Args:
            file_path: File path in storage (key)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            logger.info(f"✅ File deleted: {file_path}")
            return True

        except ClientError as e:
            logger.error(f"❌ Delete failed: {e}")
            return False

    def generate_presigned_url(
        self,
        file_path: str,
        expiration: int = 3600
    ) -> Optional[str]:
        """
        Generate a presigned URL for file access.

        Args:
            file_path: File path in storage (key)
            expiration: URL expiration time in seconds (default: 1 hour)

        Returns:
            str: Presigned URL or None if generation fails
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_path
                },
                ExpiresIn=expiration
            )
            return url

        except ClientError as e:
            logger.error(f"❌ Presigned URL generation failed: {e}")
            return None

    def list_files(self, folder: str = None, max_keys: int = 1000) -> list:
        """
        List files in a folder.

        Args:
            folder: Folder path in bucket (default: uses AWS_STORAGE_FOLDER from env)
            max_keys: Maximum number of files to return

        Returns:
            list: List of file objects
        """
        try:
            # Use default folder if not specified
            if folder is None:
                folder = self.default_folder

            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=folder,
                MaxKeys=max_keys
            )

            files = response.get('Contents', [])
            logger.info(f"✅ Listed {len(files)} files from {folder}")
            return files

        except ClientError as e:
            logger.error(f"❌ List files failed: {e}")
            return []

    def get_public_url(self, file_path: str) -> str:
        """
        Get public URL for a file (if bucket is public).

        Args:
            file_path: File path in storage (key)

        Returns:
            str: Public URL
        """
        return f"{self.endpoint}/{self.bucket_name}/{file_path}"


# Singleton instance
_storage_client = None


def get_storage_client() -> S3StorageClient:
    """
    Get or create AWS S3 Storage client singleton.

    Returns:
        S3StorageClient: Storage client instance
    """
    global _storage_client
    if _storage_client is None:
        _storage_client = S3StorageClient()
    return _storage_client
