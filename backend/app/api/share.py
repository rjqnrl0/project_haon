import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.core.errors import NotFoundError
from app.models.fitting_task import FittingTask
from app.models.share_link import ShareLink
from app.models.user import User
from app.services.share_service import ShareService

router = APIRouter(prefix="/share", tags=["share"])
share_service = ShareService()


class DownloadRequest(BaseModel):
    source_task_id: str


class ShareRequest(BaseModel):
    source_task_id: str


@router.post("/download")
async def download_image(
    body: DownloadRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await share_service.create_download(user=user, source_task_id=body.source_task_id, db=db)


@router.post("/create")
async def create_share_link(
    body: ShareRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await share_service.create_share_link(user=user, source_task_id=body.source_task_id, db=db)


@router.get("/{share_token}")
async def get_shared_image(share_token: str, db: AsyncSession = Depends(get_db)):
    return await share_service.get_shared_image(share_token=share_token, db=db)
