import io
import logging
from datetime import datetime, timedelta, timezone

import httpx
from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import NotFoundError, ValidationError
from app.models.fitting_task import FittingTask
from app.models.user import User
from app.services.file_manager import FileManagerService

logger = logging.getLogger("v-suitcase.background")


class BackgroundService:
    def __init__(self):
        self.file_manager = FileManagerService()
        self.settings = get_settings()

    async def search_unsplash(self, prompt: str) -> list[dict]:
        if not prompt.strip():
            raise ValidationError("프롬프트를 입력해주세요")

        if not self.settings.unsplash_access_key:
            return [{"id": "mock", "url": "", "thumbnail": "", "description": "Mock 배경", "photographer": "Mock"}]

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.unsplash.com/search/photos",
                params={"query": prompt, "per_page": 5, "orientation": "portrait"},
                headers={"Authorization": f"Client-ID {self.settings.unsplash_access_key}"},
            )

        if resp.status_code != 200:
            return []

        results = resp.json().get("results", [])
        return [
            {
                "id": r["id"],
                "url": r["urls"]["regular"],
                "thumbnail": r["urls"]["thumb"],
                "description": r.get("description") or r.get("alt_description"),
                "photographer": r["user"]["name"],
            }
            for r in results
        ]

    async def generate_from_text(
        self, user: User, source_task_id: str, prompt: str, db: AsyncSession
    ) -> dict:
        task = await self._get_source_task(user, source_task_id, db)
        backgrounds = await self.search_unsplash(prompt)

        if not backgrounds or not backgrounds[0].get("url"):
            # Mock: return original result
            result_url = self.file_manager.get_download_url(task.result_file_path)
            return {"task_id": str(task.id), "result_url": result_url, "background_source": "mock"}

        # Phase 1: simple overlay (return original as mock)
        result_url = self.file_manager.get_download_url(task.result_file_path)
        return {
            "task_id": str(task.id),
            "result_url": result_url,
            "background_source": backgrounds[0]["url"],
            "backgrounds": backgrounds,
        }

    async def generate_from_upload(
        self, user: User, source_task_id: str, image_bytes: bytes, content_type: str, db: AsyncSession
    ) -> dict:
        self.file_manager.validate_file(content_type, len(image_bytes))
        task = await self._get_source_task(user, source_task_id, db)

        # Phase 1: simple overlay mock — return original result
        result_url = self.file_manager.get_download_url(task.result_file_path)
        return {"task_id": str(task.id), "result_url": result_url, "background_source": "upload"}

    async def _get_source_task(self, user: User, task_id: str, db: AsyncSession) -> FittingTask:
        result = await db.execute(
            select(FittingTask).where(
                FittingTask.id == task_id,
                FittingTask.user_id == user.id,
                FittingTask.status == "completed",
            )
        )
        task = result.scalar_one_or_none()
        if not task or not task.result_file_path:
            raise NotFoundError("피팅 결과를 찾을 수 없습니다")
        return task
