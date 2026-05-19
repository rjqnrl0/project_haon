from fastapi import APIRouter, Depends, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services.fitting_service import FittingService

router = APIRouter(prefix="/fitting", tags=["fitting"])
fitting_service = FittingService()


class FittingRequest(BaseModel):
    body_image_id: str
    clothing_ids: list[str]


class FittingWithBackgroundRequest(BaseModel):
    body_image_id: str
    clothing_ids: list[str]
    product_ids: list[str] = []
    attraction: str
    destination: str


@router.post("/body/upload")
async def upload_body(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    image_bytes = await file.read()
    return await fitting_service.upload_body_image(
        user=user,
        image_bytes=image_bytes,
        content_type=file.content_type or "image/jpeg",
        db=db,
    )


@router.post("/clothing/upload")
async def upload_clothing(
    file: UploadFile = File(...),
    category: str = Form(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    image_bytes = await file.read()
    return await fitting_service.upload_clothing_image(
        user=user,
        image_bytes=image_bytes,
        content_type=file.content_type or "image/jpeg",
        category=category,
        db=db,
    )


@router.post("/execute")
async def execute_fitting(
    body: FittingRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await fitting_service.execute_fitting(
        user=user,
        body_image_id=body.body_image_id,
        clothing_ids=body.clothing_ids,
        db=db,
    )


@router.post("/execute-with-background")
async def execute_fitting_with_background(
    body: FittingWithBackgroundRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await fitting_service.execute_fitting_with_background(
        user=user,
        body_image_id=body.body_image_id,
        clothing_ids=body.clothing_ids,
        product_ids=body.product_ids,
        attraction=body.attraction,
        destination=body.destination,
        db=db,
    )


@router.get("/result/{task_id}")
async def get_result(
    task_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await fitting_service.get_fitting_result(user=user, task_id=task_id, db=db)
