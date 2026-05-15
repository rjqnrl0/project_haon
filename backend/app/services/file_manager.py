import logging
import uuid
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

from app.core.config import get_settings

logger = logging.getLogger("v-suitcase.file_manager")

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


class FileManagerService:
    def __init__(self):
        self.settings = get_settings()
        self.s3 = boto3.client("s3", region_name=self.settings.s3_region)
        self.bucket = self.settings.s3_temp_bucket

    def validate_file(self, content_type: str, size_bytes: int) -> None:
        from app.core.errors import FileTooLargeError, FileTypeInvalidError

        if content_type not in ALLOWED_CONTENT_TYPES:
            raise FileTypeInvalidError(
                f"지원하지 않는 파일 형식입니다: {content_type}"
            )
        if size_bytes > MAX_FILE_SIZE:
            raise FileTooLargeError()

    def upload_file(
        self, user_id: str, task_id: str, file_bytes: bytes, content_type: str, category: str
    ) -> str:
        ext = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}[content_type]
        s3_key = (
            f"{self.settings.env}/{user_id}/{task_id}/{category}_{uuid.uuid4().hex[:8]}.{ext}"
        )
        self.s3.put_object(
            Bucket=self.bucket,
            Key=s3_key,
            Body=file_bytes,
            ContentType=content_type,
        )
        logger.info("Uploaded %s (%d bytes)", s3_key, len(file_bytes))
        return s3_key

    def get_download_url(self, s3_key: str, expires_in: int = 900) -> str:
        from app.core.errors import NotFoundError

        try:
            self.s3.head_object(Bucket=self.bucket, Key=s3_key)
        except ClientError:
            raise NotFoundError("파일을 찾을 수 없습니다")

        return self.s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": s3_key},
            ExpiresIn=expires_in,
        )

    def delete_file(self, s3_key: str) -> None:
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=s3_key)
        except ClientError as e:
            logger.warning("Failed to delete %s: %s", s3_key, e)

    def get_file_bytes(self, s3_key: str) -> bytes:
        from app.core.errors import NotFoundError

        try:
            response = self.s3.get_object(Bucket=self.bucket, Key=s3_key)
            return response["Body"].read()
        except ClientError:
            raise NotFoundError("파일을 찾을 수 없습니다")
