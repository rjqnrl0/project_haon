import hashlib
import io
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
import numpy as np
from PIL import Image, ImageFilter
from rembg import remove as rembg_remove
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import NotFoundError, ValidationError
from app.models.fitting_task import FittingTask
from app.models.user import User
from app.services.file_manager import FileManagerService

logger = logging.getLogger("v-suitcase.fitting")

CATEGORY_TO_GARMENT_TYPE = {
    "top": "upper_body",
    "bottom": "lower_body",
    "dress": "dresses",
    "outer": "upper_body",
    "accessory": "upper_body",
}


class FittingService:
    def __init__(self):
        self.file_manager = FileManagerService()
        self.settings = get_settings()

    def _get_gemini_client(self):
        from google import genai
        return genai.Client(api_key=self.settings.gemini_api_key)

    def _gemini_generate_with_retry(self, client, **kwargs):
        import time
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return client.models.generate_content(**kwargs)
            except Exception as e:
                if attempt < max_retries - 1 and ("500" in str(e) or "503" in str(e)):
                    time.sleep(2 ** attempt)
                    continue
                raise

    def _run_gemini_tryon(self, person_bytes: bytes, garment_bytes: bytes, category: str) -> bytes:
        from google.genai import types

        client = self._get_gemini_client()

        person_img = Image.open(io.BytesIO(person_bytes)).convert("RGB")
        person_img.thumbnail((1024, 1024), Image.LANCZOS)
        buf = io.BytesIO()
        person_img.save(buf, format="PNG")
        person_png = buf.getvalue()

        garment_img = Image.open(io.BytesIO(garment_bytes)).convert("RGB")
        garment_img.thumbnail((1024, 1024), Image.LANCZOS)
        buf = io.BytesIO()
        garment_img.save(buf, format="PNG")
        garment_png = buf.getvalue()

        garment_desc = {
            "top": "상의(top)",
            "bottom": "하의(bottom/pants)",
            "dress": "원피스(dress)",
            "outer": "아우터(outer/jacket)",
            "accessory": "액세서리",
        }.get(category, "의류")

        prompt = (
            f"이 사람 사진에 두 번째 이미지의 {garment_desc}를 자연스럽게 입혀주세요. "
            f"사람의 체형, 포즈, 얼굴을 그대로 유지하면서 의류만 교체해주세요. "
            f"의류의 색상, 패턴, 디자인을 정확하게 반영하고, 조명과 그림자를 자연스럽게 처리해주세요. "
            f"배경은 깔끔한 흰색으로 해주세요."
        )

        response = self._gemini_generate_with_retry(
            client,
            model="gemini-3.1-flash-image-preview",
            contents=[
                prompt,
                types.Part.from_bytes(data=person_png, mime_type="image/png"),
                types.Part.from_bytes(data=garment_png, mime_type="image/png"),
            ],
            config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                return part.inline_data.data

        raise ValidationError("Gemini 응답에 이미지가 없습니다")

    def _run_gemini_tryon_with_background(
        self, person_bytes: bytes, garment_bytes: bytes, category: str,
        attraction: str, destination: str, weather_condition: str = "Clear"
    ) -> bytes:
        from google.genai import types

        client = self._get_gemini_client()

        person_img = Image.open(io.BytesIO(person_bytes)).convert("RGB")
        person_img.thumbnail((1024, 1024), Image.LANCZOS)
        buf = io.BytesIO()
        person_img.save(buf, format="PNG")
        person_png = buf.getvalue()

        garment_img = Image.open(io.BytesIO(garment_bytes)).convert("RGB")
        garment_img.thumbnail((1024, 1024), Image.LANCZOS)
        buf = io.BytesIO()
        garment_img.save(buf, format="PNG")
        garment_png = buf.getvalue()

        garment_desc = {
            "top": "상의(top)",
            "bottom": "하의(bottom/pants)",
            "dress": "원피스(dress)",
            "outer": "아우터(outer/jacket)",
            "accessory": "액세서리",
        }.get(category, "의류")

        weather_scene = {
            "Rain": "비가 오는 날씨, 젖은 바닥, 흐린 하늘",
            "Drizzle": "이슬비가 내리는 날씨, 흐린 하늘",
            "Thunderstorm": "뇌우가 치는 날씨, 어두운 하늘",
            "Snow": "눈이 내리는 겨울 날씨, 눈 쌓인 배경",
            "Clouds": "흐린 날씨, 구름 많은 하늘",
            "Mist": "안개 낀 아침 분위기",
            "Fog": "안개 짙은 날씨",
            "Clear": "맑고 화창한 날씨, 파란 하늘",
            "Haze": "연무가 있는 날씨, 따뜻한 분위기",
        }.get(weather_condition, "자연스러운 날씨")

        prompt = (
            f"이 사람 사진에 두 번째 이미지의 {garment_desc}를 자연스럽게 입혀주세요. "
            f"사람의 체형, 포즈, 얼굴을 그대로 유지하면서 의류만 교체해주세요. "
            f"의류의 색상, 패턴, 디자인을 정확하게 반영하고, 조명과 그림자를 자연스럽게 처리해주세요. "
            f"배경은 {destination}의 {attraction} 관광지로 합성해주세요. "
            f"날씨는 {weather_scene}으로 표현해주세요. "
            f"사람이 실제로 그 장소에 서 있는 것처럼 자연스럽게 만들어주세요."
        )

        response = self._gemini_generate_with_retry(
            client,
            model="gemini-3.1-flash-image-preview",
            contents=[
                prompt,
                types.Part.from_bytes(data=person_png, mime_type="image/png"),
                types.Part.from_bytes(data=garment_png, mime_type="image/png"),
            ],
            config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                return part.inline_data.data

        raise ValidationError("Gemini 응답에 이미지가 없습니다")

    def _restore_face(self, original_bytes: bytes, modified_bytes: bytes) -> bytes:
        orig_img = Image.open(io.BytesIO(original_bytes)).convert("RGBA")
        mod_img = Image.open(io.BytesIO(modified_bytes)).convert("RGB")
        mod_img = mod_img.resize(orig_img.size, Image.LANCZOS)

        person_no_bg = rembg_remove(orig_img)
        alpha = np.array(person_no_bg.split()[3])
        person_mask = alpha > 30

        h, w = alpha.shape
        head_bottom = int(h * 0.18)

        face_mask = np.zeros((h, w), dtype=np.uint8)
        face_mask[:head_bottom, :] = 255
        face_mask[~person_mask] = 0

        face_mask_img = Image.fromarray(face_mask, mode="L")
        face_mask_img = face_mask_img.filter(ImageFilter.GaussianBlur(radius=8))

        orig_rgb = orig_img.convert("RGB")
        result = Image.composite(orig_rgb, mod_img, face_mask_img)

        buf = io.BytesIO()
        result.save(buf, format="PNG")
        return buf.getvalue()

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

    async def execute_fitting(
        self, user: User, body_image_id: str, clothing_ids: list, db: AsyncSession
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

            try:
                current_image_bytes = self._run_gemini_tryon(
                    current_image_bytes, clothing_bytes, category
                )
            except Exception as e:
                logger.error("Gemini VTON failed for clothing %s: %s", clothing_id, e)
                raise ValidationError(f"AI 피팅 처리 실패: {str(e)}")

        current_image_bytes = self._restore_face(body_bytes, current_image_bytes)

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

    async def execute_fitting_with_background(
        self, user: User, body_image_id: str, clothing_ids: list,
        product_ids: list, attraction: str, destination: str, db: AsyncSession,
    ) -> dict:
        from app.data.dutyfree_products import get_products_by_ids
        from app.services.recommend_service import RecommendService

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

        # destination으로 실시간 날씨 조회
        weather_condition = "Clear"
        try:
            recommend_svc = RecommendService()
            dest_city_map = {
                "tokyo": "Tokyo,JP", "bangkok": "Bangkok,TH", "paris": "Paris,FR",
                "london": "London,GB", "new york": "New York,US", "bali": "Denpasar,ID",
            }
            city = dest_city_map.get(destination.lower(), destination)
            weather_data = await recommend_svc._fetch_weather(city)
            if weather_data:
                weather_condition = weather_data.get("condition", "Clear")
            logger.info("Fitting weather for %s: %s", destination, weather_condition)
        except Exception as e:
            logger.warning("Weather fetch failed for fitting, using Clear: %s", e)

        body_bytes = self.file_manager.get_file_bytes(task.body_file_path)
        current_image_bytes = body_bytes

        fitting_items = []
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
            fitting_items.append(clothing_task)

        fitting_items.sort(
            key=lambda x: {"bottom": 0, "top": 1, "dress": 1, "outer": 2}.get(
                x.task_type or "top", 1
            )
        )

        for idx, clothing_task in enumerate(fitting_items):
            category = clothing_task.task_type or "top"
            clothing_bytes = self.file_manager.get_file_bytes(clothing_task.body_file_path)

            is_last = idx == len(fitting_items) - 1

            try:
                if is_last and attraction and destination:
                    current_image_bytes = self._run_gemini_tryon_with_background(
                        current_image_bytes, clothing_bytes, category,
                        attraction, destination, weather_condition
                    )
                else:
                    current_image_bytes = self._run_gemini_tryon(
                        current_image_bytes, clothing_bytes, category
                    )
            except Exception as e:
                logger.error("Gemini VTON failed for %s: %s", category, e)
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

        clothing_info = get_products_by_ids(product_ids) if product_ids else []

        return {
            "task_id": str(task.id),
            "status": "completed",
            "result_url": self.file_manager.get_download_url(result_s3_key),
            "clothing_info": clothing_info,
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
