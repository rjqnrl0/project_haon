import base64
import hashlib
import io
import json
import logging
import uuid
from datetime import datetime, timedelta, timezone

import boto3
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

CATEGORY_BODY_REGIONS = {
    "top": (0.15, 0.55),
    "bottom": (0.45, 0.95),
    "dress": (0.15, 0.85),
    "outer": (0.10, 0.60),
    "accessory": (0.0, 0.2),
}


class FittingService:
    def __init__(self):
        self.file_manager = FileManagerService()
        self.settings = get_settings()
        session = boto3.Session()
        self.bedrock = session.client("bedrock-runtime", region_name="us-east-1")

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
            "max_tokens": 500,
            "messages": [{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": "image/png", "data": image_b64},
                    },
                    {
                        "type": "text",
                        "text": "You are a fashion product photographer writing an exact visual specification for an AI image generator to reproduce this garment identically. "
                                "Analyze the image with EXTREME precision. You MUST cover ALL of the following:\n\n"
                                "1. GARMENT TYPE: exact type (e.g., crew-neck t-shirt, double-breasted blazer, A-line midi skirt)\n"
                                "2. COLOR (CRITICAL - be extremely precise): "
                                "- Primary color: use specific shade names (e.g., 'bright cherry red', 'deep navy blue', 'ivory white')\n"
                                "- Secondary colors: list all additional colors visible\n"
                                "- Color distribution: what percentage of the garment is each color\n"
                                "- Color temperature: warm/cool/neutral\n"
                                "3. PATTERN (if any): solid/striped/plaid/floral/graphic/geometric\n"
                                "- Pattern scale: tiny/small/medium/large/oversized\n"
                                "- Pattern colors: list each color in the pattern\n"
                                "- Pattern spacing and repetition\n"
                                "- For florals: flower type, size, arrangement\n"
                                "4. MATERIAL APPEARANCE: matte/glossy/satin/textured — how does light interact with the surface\n"
                                "5. CONSTRUCTION: collar type, neckline, sleeve length, cuff style, hem, closure (buttons/zipper/none), seam details\n"
                                "6. FIT & SILHOUETTE: slim/regular/oversized, cropped/standard/longline, structured/relaxed, body-skimming/flowing\n"
                                "7. DISTINCTIVE FEATURES: logos, embroidery, hardware, contrast stitching, pockets, pleats, ruffles, cutouts\n\n"
                                "Output format: Write a single dense paragraph starting with garment type. "
                                "Prioritize COLOR and PATTERN accuracy above all else — these are the most critical for visual reproduction. "
                                "Do NOT mention any person, body, mannequin, hanger, or background.",
                    },
                ],
            }],
        })

        response = self.bedrock.invoke_model(
            modelId="us.anthropic.claude-sonnet-4-6",
            contentType="application/json",
            accept="application/json",
            body=body,
        )

        resp_body = json.loads(response["body"].read())
        return resp_body["content"][0]["text"]

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

    def _generate_background_mask(self, body_bytes: bytes) -> bytes:
        img = Image.open(io.BytesIO(body_bytes)).convert("RGBA")
        person_no_bg = rembg_remove(img)

        alpha = np.array(person_no_bg.split()[3])
        person_mask = alpha > 30

        bg_mask = np.where(person_mask, 0, 255).astype(np.uint8)

        mask_img = Image.fromarray(bg_mask, mode="L")
        mask_img = mask_img.filter(ImageFilter.GaussianBlur(radius=5))
        mask_rgb = Image.merge("RGB", [mask_img, mask_img, mask_img])

        buf = io.BytesIO()
        mask_rgb.save(buf, format="PNG")
        return buf.getvalue()

    def _generate_clothing_mask(self, body_bytes: bytes, category: str) -> bytes:
        img = Image.open(io.BytesIO(body_bytes)).convert("RGBA")
        person_no_bg = rembg_remove(img)

        alpha = np.array(person_no_bg.split()[3])
        person_mask = alpha > 30

        h, w = alpha.shape
        top_ratio, bottom_ratio = CATEGORY_BODY_REGIONS.get(category, (0.15, 0.85))
        top_y = int(h * top_ratio)
        bottom_y = int(h * bottom_ratio)

        clothing_mask = np.zeros((h, w), dtype=np.uint8)
        clothing_mask[top_y:bottom_y, :] = 255

        clothing_mask[~person_mask] = 0

        skin_margin_x = int(w * 0.15)
        clothing_mask[:, :skin_margin_x] = 0
        clothing_mask[:, w - skin_margin_x:] = 0

        head_bottom = int(h * 0.15)
        clothing_mask[:head_bottom, :] = 0

        mask_img = Image.fromarray(clothing_mask, mode="L")
        mask_img = mask_img.filter(ImageFilter.GaussianBlur(radius=3))
        mask_rgb = Image.merge("RGB", [mask_img, mask_img, mask_img])

        buf = io.BytesIO()
        mask_rgb.save(buf, format="PNG")
        return buf.getvalue()

    def _invoke_inpaint(self, image_bytes: bytes, mask_bytes: bytes, prompt: str) -> bytes:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img.thumbnail((1024, 1024), Image.LANCZOS)
        w, h = img.size
        w = max(256, (w // 64) * 64)
        h = max(256, (h // 64) * 64)
        img = img.resize((w, h), Image.LANCZOS)
        target_size = (w, h)

        mask_img = Image.open(io.BytesIO(mask_bytes)).convert("RGB")
        mask_img = mask_img.resize(target_size, Image.LANCZOS)

        img_buf = io.BytesIO()
        img.save(img_buf, format="PNG")
        image_b64 = base64.b64encode(img_buf.getvalue()).decode()

        mask_buf = io.BytesIO()
        mask_img.save(mask_buf, format="PNG")
        mask_b64 = base64.b64encode(mask_buf.getvalue()).decode()

        body = json.dumps({
            "taskType": "INPAINTING",
            "inPaintingParams": {
                "image": image_b64,
                "maskImage": mask_b64,
                "text": prompt,
            },
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "width": target_size[0],
                "height": target_size[1],
                "quality": "premium",
            },
        })

        response = self.bedrock.invoke_model(
            modelId="amazon.nova-canvas-v1:0",
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

            mask_bytes = self._generate_clothing_mask(current_image_bytes, category)
            inpaint_prompt = (
                f"A person wearing {clothing_description}. "
                f"The garment fits naturally on the body. Photorealistic, same lighting and perspective."
            )

            try:
                current_image_bytes = self._invoke_inpaint(
                    current_image_bytes, mask_bytes, inpaint_prompt
                )
            except Exception as e:
                logger.error("Bedrock inpaint failed for clothing %s: %s", clothing_id, e)
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
        self, user: User, body_image_id: str, clothing_ids: list[str],
        product_ids: list[str], attraction: str, destination: str, db: AsyncSession
    ) -> dict:
        from app.data.dutyfree_products import get_products_by_ids

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

        products = get_products_by_ids(product_ids) if product_ids else []
        product_by_index = {i: p for i, p in enumerate(products)}

        fitting_items = []
        for idx, clothing_id in enumerate(clothing_ids):
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
            product_info = product_by_index.get(idx)
            fitting_items.append((clothing_task, product_info))

        fitting_items.sort(
            key=lambda x: {"bottom": 0, "top": 1, "dress": 1, "outer": 2}.get(
                x[0].task_type or "top", 1
            )
        )

        for clothing_task, product_info in fitting_items:
            category = clothing_task.task_type or "top"

            if product_info and product_info.get("image_prompt"):
                clothing_description = product_info["image_prompt"]
            elif product_info:
                clothing_bytes = self.file_manager.get_file_bytes(clothing_task.body_file_path)
                clothing_description = self._describe_clothing(clothing_bytes)
            else:
                clothing_bytes = self.file_manager.get_file_bytes(clothing_task.body_file_path)
                clothing_description = self._describe_clothing(clothing_bytes)

            logger.info("Fitting %s: %s", category, clothing_description)

            mask_bytes = self._generate_clothing_mask(current_image_bytes, category)
            inpaint_prompt = (
                f"A person wearing {clothing_description}. "
                f"The garment fits naturally on the body. Photorealistic, same lighting and perspective."
            )

            try:
                current_image_bytes = self._invoke_inpaint(
                    current_image_bytes, mask_bytes, inpaint_prompt
                )
            except Exception as e:
                logger.error("Bedrock inpaint failed for %s: %s", category, e)
                raise ValidationError(f"AI 피팅 처리 실패: {str(e)}")

        current_image_bytes = self._restore_face(body_bytes, current_image_bytes)

        bg_mask_bytes = self._generate_background_mask(current_image_bytes)
        bg_prompt = (
            f"A beautiful outdoor scene at {attraction} in {destination}, "
            f"famous landmark clearly visible in the background, "
            f"natural daylight, travel photography, realistic perspective, "
            f"ground level view with pavement or path under feet"
        )
        logger.info("Background inpaint prompt: %s", bg_prompt)

        try:
            current_image_bytes = self._invoke_inpaint(
                current_image_bytes, bg_mask_bytes, bg_prompt
            )
        except Exception as e:
            logger.warning("Background inpaint failed, keeping original: %s", e)

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
