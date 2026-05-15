import hashlib
import io
import logging
import uuid
from datetime import datetime, timedelta, timezone

from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import NotFoundError, ValidationError
from app.models.fitting_task import FittingTask
from app.models.user import User
from app.services.file_manager import FileManagerService

logger = logging.getLogger("v-suitcase.fitting")

CATEGORY_POSITIONS = {
    "top": {"y_start": 0.30, "y_end": 0.55, "width_ratio": 0.60},
    "bottom": {"y_start": 0.50, "y_end": 0.80, "width_ratio": 0.55},
    "dress": {"y_start": 0.30, "y_end": 0.80, "width_ratio": 0.60},
    "outer": {"y_start": 0.30, "y_end": 0.55, "width_ratio": 0.65},
    "accessory": {"y_start": 0.20, "y_end": 0.30, "width_ratio": 0.20},
}


class FittingService:
    def __init__(self):
        self.file_manager = FileManagerService()
        self.settings = get_settings()

    async def upload_body_image(
        self, user: User, image_bytes: bytes, content_type: str, db: AsyncSession
    ) -> dict:
        self.file_manager.validate_file(content_type, len(image_bytes))

        img = Image.open(io.BytesIO(image_bytes))
        if img.width < 640 or img.height < 480:
            raise ValidationError("이미지 해상도가 최소 640x480 이상이어야 합니다")

        task_id = str(uuid.uuid4())
        s3_key = self.file_manager.upload_file(
            user_id=str(user.id),
            task_id=task_id,
            file_bytes=image_bytes,
            content_type=content_type,
            category="body",
        )

        file_hash = hashlib.md5(image_bytes).hexdigest()

        task = FittingTask(
            user_id=user.id,
            task_type="fitting",
            status="pending",
            body_file_path=s3_key,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=self.settings.file_expiry_hours),
        )
        db.add(task)
        await db.flush()

        return {
            "task_id": str(task.id),
            "body_s3_key": s3_key,
            "file_hash": file_hash,
            "width": img.width,
            "height": img.height,
        }

    async def upload_clothing_image(
        self, user: User, image_bytes: bytes, content_type: str, category: str, db: AsyncSession
    ) -> dict:
        self.file_manager.validate_file(content_type, len(image_bytes))

        valid_categories = ["top", "bottom", "dress", "outer", "accessory"]
        if category not in valid_categories:
            raise ValidationError(f"유효하지 않은 카테고리: {category}")

        clothing_id = str(uuid.uuid4())
        s3_key = self.file_manager.upload_file(
            user_id=str(user.id),
            task_id=clothing_id,
            file_bytes=image_bytes,
            content_type=content_type,
            category=f"clothing_{category}",
        )

        return {
            "clothing_id": clothing_id,
            "s3_key": s3_key,
            "category": category,
        }

    async def execute_fitting(
        self, user: User, body_image_id: str, clothing_ids: list[str], db: AsyncSession
    ) -> dict:
        result = await db.execute(
            select(FittingTask).where(
                FittingTask.id == body_image_id,
                FittingTask.user_id == user.id,
            )
        )
        task = result.scalar_one_or_none()
        if not task:
            raise NotFoundError("전신 사진을 찾을 수 없습니다")

        task.status = "processing"
        await db.flush()

        # Phase 1 Mock: overlay clothing on body
        body_bytes = self.file_manager.get_file_bytes(task.body_file_path)
        body_img = Image.open(io.BytesIO(body_bytes)).convert("RGBA")

        for clothing_id in clothing_ids:
            # In real impl, lookup clothing S3 key from storage
            # Phase 1: just use body image as-is (mock)
            pass

        # Save result (Phase 1: return body as result)
        result_buffer = io.BytesIO()
        body_img.convert("RGB").save(result_buffer, format="JPEG", quality=85)
        result_bytes = result_buffer.getvalue()

        result_s3_key = self.file_manager.upload_file(
            user_id=str(user.id),
            task_id=str(task.id),
            file_bytes=result_bytes,
            content_type="image/jpeg",
            category="result",
        )

        task.result_file_path = result_s3_key
        task.status = "completed"
        await db.flush()

        return {
            "task_id": str(task.id),
            "status": "completed",
            "result_url": self.file_manager.get_download_url(result_s3_key),
        }

    async def get_fitting_result(self, user: User, task_id: str, db: AsyncSession) -> dict:
        result = await db.execute(
            select(FittingTask).where(
                FittingTask.id == task_id,
                FittingTask.user_id == user.id,
            )
        )
        task = result.scalar_one_or_none()
        if not task:
            raise NotFoundError("피팅 결과를 찾을 수 없습니다")

        result_url = None
        if task.result_file_path:
            result_url = self.file_manager.get_download_url(task.result_file_path)

        return {
            "task_id": str(task.id),
            "status": task.status,
            "result_url": result_url,
        }
