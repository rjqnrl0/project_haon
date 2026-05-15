import io
import logging
import uuid
from datetime import datetime, timedelta, timezone

from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import NotFoundError
from app.models.fitting_task import FittingTask
from app.models.share_link import ShareLink
from app.models.user import User
from app.services.file_manager import FileManagerService

logger = logging.getLogger("v-suitcase.share")


class ShareService:
    def __init__(self):
        self.file_manager = FileManagerService()
        self.settings = get_settings()

    def _add_watermark(self, image_bytes: bytes) -> bytes:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")

        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        font_size = max(int(img.width * 0.03), 12)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        except (OSError, IOError):
            font = ImageFont.load_default()

        text = "V-Suitcase"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = img.width - text_width - 10
        y = img.height - text_height - 10

        # Shadow
        draw.text((x + 1, y + 1), text, fill=(0, 0, 0, 102), font=font)
        # Main text
        draw.text((x, y), text, fill=(255, 255, 255, 102), font=font)

        result = Image.alpha_composite(img, overlay)
        output = io.BytesIO()
        result.convert("RGB").save(output, format="JPEG", quality=85)
        return output.getvalue()

    async def create_download(self, user: User, source_task_id: str, db: AsyncSession) -> dict:
        task = await self._get_task(user, source_task_id, db)
        image_bytes = self.file_manager.get_file_bytes(task.result_file_path)
        watermarked = self._add_watermark(image_bytes)

        s3_key = self.file_manager.upload_file(
            user_id=str(user.id),
            task_id=str(task.id),
            file_bytes=watermarked,
            content_type="image/jpeg",
            category="watermarked",
        )

        download_url = self.file_manager.get_download_url(s3_key)
        return {"download_url": download_url, "filename": f"vsuitcase_fitting_{task.id}.jpg"}

    async def create_share_link(self, user: User, source_task_id: str, db: AsyncSession) -> dict:
        task = await self._get_task(user, source_task_id, db)

        image_bytes = self.file_manager.get_file_bytes(task.result_file_path)
        watermarked = self._add_watermark(image_bytes)

        share_token = str(uuid.uuid4())
        s3_key = self.file_manager.upload_file(
            user_id=str(user.id),
            task_id=share_token,
            file_bytes=watermarked,
            content_type="image/jpeg",
            category="shared",
        )

        share_link = ShareLink(
            user_id=user.id,
            share_token=share_token,
            source_task_id=task.id,
            watermarked_path=s3_key,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=self.settings.share_expiry_hours),
        )
        db.add(share_link)
        await db.flush()

        return {
            "share_token": share_token,
            "share_url": f"/share/{share_token}",
            "expires_at": share_link.expires_at.isoformat(),
        }

    async def get_shared_image(self, share_token: str, db: AsyncSession) -> dict:
        result = await db.execute(
            select(ShareLink).where(ShareLink.share_token == share_token)
        )
        link = result.scalar_one_or_none()

        if not link:
            raise NotFoundError("공유 링크를 찾을 수 없습니다")

        if link.expires_at < datetime.now(timezone.utc):
            raise NotFoundError("이 공유 링크는 만료되었습니다")

        image_url = self.file_manager.get_download_url(link.watermarked_path)
        return {
            "image_url": image_url,
            "title": "V-Suitcase 피팅 결과",
            "description": "AI 가상 피팅 결과를 확인해보세요!",
        }

    async def _get_task(self, user: User, task_id: str, db: AsyncSession) -> FittingTask:
        result = await db.execute(
            select(FittingTask).where(
                FittingTask.id == task_id,
                FittingTask.user_id == user.id,
                FittingTask.status == "completed",
            )
        )
        task = result.scalar_one_or_none()
        if not task or not task.result_file_path:
            raise NotFoundError("결과 이미지를 찾을 수 없습니다")
        return task
