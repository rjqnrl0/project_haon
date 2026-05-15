from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services.background_service import BackgroundService

router = APIRouter(prefix="/background", tags=["background"])
bg_service = BackgroundService()


class TextBackgroundRequest(BaseModel):
    source_task_id: str
    prompt: str


@router.post("/text")
async def generate_text_background(
    body: TextBackgroundRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await bg_service.generate_from_text(
        user=user, source_task_id=body.source_task_id, prompt=body.prompt, db=db
    )


@router.post("/upload/{source_task_id}")
async def generate_upload_background(
    source_task_id: str,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    image_bytes = await file.read()
    return await bg_service.generate_from_upload(
        user=user,
        source_task_id=source_task_id,
        image_bytes=image_bytes,
        content_type=file.content_type or "image/jpeg",
        db=db,
    )


@router.get("/search")
async def search_backgrounds(prompt: str):
    return await bg_service.search_unsplash(prompt)
