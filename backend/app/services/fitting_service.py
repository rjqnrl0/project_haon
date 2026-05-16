import base64
import hashlib
import io
import json
import logging
import uuid
from datetime import datetime, timedelta, timezone

import boto3
from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import NotFoundError, ValidationError
from app.models.fitting_task import FittingTask
from app.models.user import User
from app.services.file_manager import FileManagerService

logger = logging.getLogger("v-suitcase.fitting")

CATEGORY_SEARCH_TERMS = {
    "top": "the shirt or top on the torso",
    "bottom": "the pants or skirt on the legs",
    "dress": "the clothing on the body from shoulders to knees",
    "outer": "the jacket or coat on the upper body",
    "accessory": "the accessory",
}


class FittingService:
    def __init__(self):
        self.file_manager = FileManagerService()
        self.settings = get_settings()
        self.bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

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

        task = FittingTask(
            id=uuid.UUID(clothing_id),
            user_id=user.id,
            task_type=category,
            status="uploaded",
            body_file_path=s3_key,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=self.settings.file_expiry_hours),
        )
        db.add(task)
        await db.flush()

        return {
            "clothing_id": clothing_id,
            "s3_key": s3_key,
            "category": category,
        }

    def _describe_clothing(self, clothing_bytes: bytes) -> str:
        img = Image.open(io.BytesIO(clothing_bytes)).convert("RGB")
        img.thumbnail((512, 512), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        image_b64 = base64.b64encode(buf.getvalue()).decode()

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 300,
            "messages": [{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": "image/png", "data": image_b64},
                    },
                    {
                        "type": "text",
                        "text": "Describe ONLY this clothing item in detail for an AI image generator. "
                                "Include: type of garment, color, pattern, material texture, style, fit, and distinctive features. "
                                "Be specific and concise in 1-2 sentences. "
                                "Do NOT describe any person, body, face, or background. Only the garment itself.",
                    },
                ],
            }],
        })

        response = self.bedrock.invoke_model(
            modelId="us.anthropic.claude-opus-4-6-v1",
            contentType="application/json",
            accept="application/json",
            body=body,
        )

        resp_body = json.loads(response["body"].read())
        return resp_body["content"][0]["text"]

    def _invoke_search_replace(self, image_bytes: bytes, search_prompt: str, replace_prompt: str) -> bytes:
        img = Image.open(io.BytesIO(image_bytes))
        img = img.convert("RGB")
        img.thumbnail((1024, 1024), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        image_b64 = base64.b64encode(buf.getvalue()).decode()

        body = json.dumps({
            "image": image_b64,
            "search_prompt": search_prompt,
            "prompt": replace_prompt,
        })

        response = self.bedrock.invoke_model(
            modelId="us.stability.stable-image-search-replace-v1:0",
            contentType="application/json",
            accept="application/json",
            body=body,
        )

        response_body = json.loads(response["body"].read())
        result_b64 = response_body["images"][0]
        return base64.b64decode(result_b64)

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

        body_bytes = self.file_manager.get_file_bytes(task.body_file_path)

        current_image_bytes = body_bytes
        for clothing_id in clothing_ids:
            clothing_result = await db.execute(
                select(FittingTask).where(
                    FittingTask.id == clothing_id,
                    FittingTask.user_id == user.id,
                )
            )
            clothing_task = clothing_result.scalar_one_or_none()
            if not clothing_task or not clothing_task.body_file_path:
                logger.warning("Clothing task %s not found, skipping", clothing_id)
                continue

            category = clothing_task.task_type or "top"
            clothing_bytes = self.file_manager.get_file_bytes(clothing_task.body_file_path)

            clothing_description = self._describe_clothing(clothing_bytes)
            logger.info("Clothing description for %s: %s", clothing_id, clothing_description)

            search_term = CATEGORY_SEARCH_TERMS.get(category, "the clothing on the person")
            replace_prompt = f"{clothing_description}, same person same pose same background"

            try:
                current_image_bytes = self._invoke_search_replace(
                    current_image_bytes, search_term, replace_prompt
                )
            except Exception as e:
                logger.error("Bedrock fitting failed for clothing %s: %s", clothing_id, e)
                raise ValidationError(f"AI 피팅 처리 실패: {str(e)}")

        result_s3_key = self.file_manager.upload_file(
            user_id=str(user.id),
            task_id=str(task.id),
            file_bytes=current_image_bytes,
            content_type="image/png",
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
