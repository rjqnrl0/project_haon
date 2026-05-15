import logging

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import NotFoundError, ValidationError
from app.models.fitting_task import FittingTask
from app.models.user import User

logger = logging.getLogger("v-suitcase.recommend")

MOCK_SIZE_RECOMMENDATION = {
    "top": {
        "recommended_size": "M",
        "size_chart": {"S": "가슴 86-91cm", "M": "가슴 91-97cm", "L": "가슴 97-102cm", "XL": "가슴 102-107cm"},
        "fit_advice": "이 상의는 레귤러핏으로, 평소 사이즈를 추천드립니다.",
        "styling_tip": "슬림핏 하의와 매치하면 균형잡힌 실루엣을 연출할 수 있습니다.",
    },
    "bottom": {
        "recommended_size": "M",
        "size_chart": {"S": "허리 71-76cm", "M": "허리 76-81cm", "L": "허리 81-86cm", "XL": "허리 86-91cm"},
        "fit_advice": "이 하의는 스탠다드핏으로, 편안한 착용감을 제공합니다.",
        "styling_tip": "깔끔한 셔츠나 니트와 매치하면 세미 캐주얼 룩을 완성할 수 있습니다.",
    },
}

WEATHER_CODI_TEMPLATES = {
    "hot": "가볍고 통기성 좋은 린넨 소재의 상의와 반바지를 추천드립니다. 자외선 차단을 위해 모자를 챙기세요.",
    "warm": "얇은 면 소재의 셔츠와 면바지가 적합합니다. 아침저녁 온도차에 대비해 가벼운 가디건을 준비하세요.",
    "cool": "니트나 스웨터에 자켓을 레이어링하세요. 스카프를 활용하면 스타일리시하면서 따뜻합니다.",
    "cold": "두꺼운 코트와 기모 안감 바지를 추천합니다. 장갑, 목도리, 비니는 필수입니다.",
}


class RecommendService:
    def __init__(self):
        self.settings = get_settings()

    async def get_size_recommendation(self, user: User, task_id: str, db: AsyncSession) -> dict:
        result = await db.execute(
            select(FittingTask).where(FittingTask.id == task_id, FittingTask.user_id == user.id)
        )
        task = result.scalar_one_or_none()
        if not task:
            raise NotFoundError("피팅 결과를 찾을 수 없습니다")

        # Phase 1: hardcoded mock
        return {
            "task_id": str(task.id),
            "recommendations": MOCK_SIZE_RECOMMENDATION,
        }

    async def get_weather_codi(self, user: User, city: str) -> dict:
        if not city.strip():
            raise ValidationError("도시명을 입력해주세요")

        weather_data = await self._fetch_weather(city)

        avg_temp = weather_data["avg_temp"] if weather_data else 20
        if avg_temp >= 30:
            template_key = "hot"
        elif avg_temp >= 20:
            template_key = "warm"
        elif avg_temp >= 10:
            template_key = "cool"
        else:
            template_key = "cold"

        codi_advice = WEATHER_CODI_TEMPLATES[template_key]

        essential_items = {
            "hot": ["선크림", "모자", "선글라스"],
            "warm": ["가디건", "우산"],
            "cool": ["자켓", "스카프"],
            "cold": ["코트", "장갑", "목도리", "비니"],
        }[template_key]

        return {
            "city": city,
            "weather": weather_data,
            "codi_advice": codi_advice,
            "essential_items": essential_items,
            "additional_tips": f"{city}에서의 여행을 즐기세요!",
        }

    async def _fetch_weather(self, city: str) -> dict | None:
        api_key = self.settings.openweathermap_api_key
        if not api_key:
            return {"avg_temp": 22, "condition": "Clear", "forecasts": [], "source": "mock"}

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.openweathermap.org/data/2.5/forecast",
                    params={"q": city, "cnt": 40, "appid": api_key, "units": "metric"},
                )
            if resp.status_code != 200:
                raise ValidationError(f"도시를 찾을 수 없습니다: {city}")

            data = resp.json()
            forecasts = []
            temps = []
            for item in data["list"][:40]:
                temps.append(item["main"]["temp"])
                forecasts.append({
                    "date": item["dt_txt"],
                    "temp": item["main"]["temp"],
                    "condition": item["weather"][0]["main"],
                    "precipitation": item.get("pop", 0) * 100,
                })

            return {
                "avg_temp": sum(temps) / len(temps) if temps else 20,
                "condition": data["list"][0]["weather"][0]["main"],
                "forecasts": forecasts[:10],
                "source": "openweathermap",
            }
        except httpx.HTTPError:
            return {"avg_temp": 22, "condition": "Clear", "forecasts": [], "source": "mock"}
