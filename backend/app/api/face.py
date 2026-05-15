from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services.face_service import FaceVerificationService

router = APIRouter(prefix="/face", tags=["face"])
face_service = FaceVerificationService()


@router.post("/register")
async def register_face(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    image_bytes = await file.read()
    return await face_service.register_face(
        user=user,
        image_bytes=image_bytes,
        content_type=file.content_type or "image/jpeg",
        db=db,
    )


@router.post("/verify")
async def verify_face(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    image_bytes = await file.read()
    return await face_service.verify_face(
        user=user,
        image_bytes=image_bytes,
        content_type=file.content_type or "image/jpeg",
    )


@router.get("/status")
async def face_status(user: User = Depends(get_current_user)):
    return {
        "face_registered": user.face_registered,
    }
