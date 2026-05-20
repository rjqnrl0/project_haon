from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services.recommend_service import RecommendService

router = APIRouter(prefix="/recommend", tags=["recommend"])
recommend_service = RecommendService()


class WeatherCodiRequest(BaseModel):
    city: str


class DutyFreeCodiRequest(BaseModel):
    destination: str
    arrival: str


class AttractionsRequest(BaseModel):
    destination: str


class WeatherSimpleRequest(BaseModel):
    destination: str
    arrival: str = ""


@router.get("/size/{task_id}")
async def get_size_recommendation(
    task_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await recommend_service.get_size_recommendation(user=user, task_id=task_id, db=db)


@router.post("/weather")
async def get_weather_codi(
    body: WeatherCodiRequest,
    user: User = Depends(get_current_user),
):
    return await recommend_service.get_weather_codi(user=user, city=body.city)


@router.post("/dutyfree-codi")
async def get_dutyfree_codi(
    body: DutyFreeCodiRequest,
    user: User = Depends(get_current_user),
):
    return await recommend_service.get_dutyfree_codi(
        user=user, destination=body.destination, arrival=body.arrival
    )


@router.post("/weather-simple")
async def get_weather_simple(
    body: WeatherSimpleRequest,
    user: User = Depends(get_current_user),
):
    return await recommend_service.get_weather_brief(
        destination=body.destination, arrival=body.arrival
    )


@router.post("/attractions")
async def get_attractions(
    body: AttractionsRequest,
    user: User = Depends(get_current_user),
):
    return await recommend_service.get_attractions(destination=body.destination)
