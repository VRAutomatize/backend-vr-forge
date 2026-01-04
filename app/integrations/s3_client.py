"""AWS S3 client for file storage."""

import io
from typing import BinaryIO, Optional

import boto3
from botocore.exceptions import ClientError

from app.core.config import get_settings
from app.core.exceptions import StorageError
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class S3Client:
    """AWS S3 client wrapper."""

    def __init__(self):
        """Initialize S3 client."""
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION,
        )
        self.bucket_name = settings.AWS_S3_BUCKET_NAME

    async def upload_file(
        self,
        file_content: bytes | BinaryIO,
        s3_key: str,
        content_type: Optional[str] = None,
    ) -> str:
        """Upload file to S3.

        Args:
            file_content: File content as bytes or file-like object
            s3_key: S3 object key
            content_type: Content type of the file

        Returns:
            S3 key of uploaded file

        Raises:
            StorageError: If upload fails
        """
        try:
            extra_args = {}
            if content_type:
                extra_args["ContentType"] = content_type

            if isinstance(file_content, bytes):
                file_content = io.BytesIO(file_content)

            self.s3_client.upload_fileobj(
                file_content,
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args,
            )

            logger.info("File uploaded to S3", s3_key=s3_key, bucket=self.bucket_name)
            return s3_key

        except ClientError as e:
            logger.error("S3 upload failed", error=str(e), s3_key=s3_key)
            raise StorageError("upload", str(e)) from e

    async def download_file(self, s3_key: str) -> bytes:
        """Download file from S3.

        Args:
            s3_key: S3 object key

        Returns:
            File content as bytes

        Raises:
            StorageError: If download fails
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            content = response["Body"].read()
            logger.info("File downloaded from S3", s3_key=s3_key)
            return content

        except ClientError as e:
            logger.error("S3 download failed", error=str(e), s3_key=s3_key)
            raise StorageError("download", str(e)) from e

    async def delete_file(self, s3_key: str) -> None:
        """Delete file from S3.

        Args:
            s3_key: S3 object key

        Raises:
            StorageError: If deletion fails
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info("File deleted from S3", s3_key=s3_key)

        except ClientError as e:
            logger.error("S3 deletion failed", error=str(e), s3_key=s3_key)
            raise StorageError("delete", str(e)) from e

    def generate_presigned_url(
        self,
        s3_key: str,
        expiration: int = 3600,
    ) -> str:
        """Generate presigned URL for file download.

        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds

        Returns:
            Presigned URL

        Raises:
            StorageError: If URL generation fails
        """
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": s3_key},
                ExpiresIn=expiration,
            )
            return url

        except ClientError as e:
            logger.error("S3 presigned URL generation failed", error=str(e), s3_key=s3_key)
            raise StorageError("presigned_url", str(e)) from e

    def file_exists(self, s3_key: str) -> bool:
        """Check if file exists in S3.

        Args:
            s3_key: S3 object key

        Returns:
            True if file exists, False otherwise
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError:
            return False

