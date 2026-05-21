import base64
import json
import logging
import uuid
from typing import Optional

import boto3
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import NotFoundError, ValidationError
from app.models.fitting_task import FittingTask
from app.models.user import User
from app.services.file_manager import FileManagerService

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

FALLBACK_TEMPLATES = {
    "hot": {
        "codi_advice": "가볍고 통기성 좋은 린넨 소재의 상의와 반바지를 추천드립니다. 자외선 차단을 위해 모자를 챙기세요.",
        "essential_items": ["선크림", "모자", "선글라스"],
        "additional_tips": "자외선 지수가 높으니 피부 보호에 신경 쓰세요.",
    },
    "warm": {
        "codi_advice": "얇은 면 소재의 셔츠와 면바지가 적합합니다. 아침저녁 온도차에 대비해 가벼운 가디건을 준비하세요.",
        "essential_items": ["가디건", "우산"],
        "additional_tips": "일교차가 있을 수 있으니 레이어링을 추천합니다.",
    },
    "cool": {
        "codi_advice": "니트나 스웨터에 자켓을 레이어링하세요. 스카프를 활용하면 스타일리시하면서 따뜻합니다.",
        "essential_items": ["자켓", "스카프"],
        "additional_tips": "바람이 불 수 있으니 방풍 소재를 추천합니다.",
    },
    "cold": {
        "codi_advice": "두꺼운 코트와 기모 안감 바지를 추천합니다. 장갑, 목도리, 비니는 필수입니다.",
        "essential_items": ["코트", "장갑", "목도리", "비니"],
        "additional_tips": "보온에 집중하되 실내 활동 시 벗기 쉬운 레이어링이 좋습니다.",
    },
}


class RecommendService:
    def __init__(self):
        self.settings = get_settings()
        session = boto3.Session()
        self.bedrock = session.client("bedrock-runtime", region_name="us-east-1")
        self.file_manager = FileManagerService()

    def _gemini_text(self, prompt: str) -> str:
        from google import genai as _genai
        from google.genai import types as _types

        client = _genai.Client(api_key=self.settings.gemini_api_key)
        response = client.models.generate_content(
            model="gemini-3.1-flash-image-preview",
            contents=prompt,
            config=_types.GenerateContentConfig(
                response_modalities=["TEXT"],
            ),
        )
        for part in response.candidates[0].content.parts:
            if hasattr(part, "text") and part.text:
                return part.text.strip()
        return ""

    def _generate_codi_with_claude(self, city: str, weather_data: dict) -> dict:
        avg_temp = weather_data.get("avg_temp", 20)
        condition = weather_data.get("condition", "Clear")
        forecasts = weather_data.get("forecasts", [])

        precipitation = 0
        if forecasts:
            precipitation = sum(f.get("precipitation", 0) for f in forecasts) / len(forecasts)

        prompt = (
            f"당신은 여행 패션 스타일리스트입니다.\n"
            f"여행지: {city}\n"
            f"날씨 정보: 평균기온 {avg_temp:.1f}°C, 날씨 상태 {condition}, 평균 강수확률 {precipitation:.0f}%\n\n"
            f"위 날씨 정보와 여행지 특성을 바탕으로 여행에 적합한 코디를 추천해주세요.\n"
            f"현지 문화와 관광지 특성도 고려해주세요.\n\n"
            f"반드시 아래 JSON 형식으로만 응답하세요 (다른 텍스트 없이):\n"
            f'{{\n'
            f'  "codi_advice": "3-4문장의 구체적인 코디 추천",\n'
            f'  "essential_items": ["필수 아이템1", "필수 아이템2", "필수 아이템3", "필수 아이템4"],\n'
            f'  "additional_tips": "여행지 특성을 반영한 실용적 팁 1문장"\n'
            f'}}'
        )

        text = self._gemini_text(prompt)

        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            text = text.rsplit("```", 1)[0].strip()

        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            text = text[start:end]

        return json.loads(text)

    def _translate_codi_to_english(self, city: str, codi_advice: str) -> str:
        prompt = (
            f"Translate the following Korean fashion recommendation into a concise English image prompt "
            f"(1-2 sentences max, describe ONLY the clothing items and style):\n\n{codi_advice}"
        )
        return self._gemini_text(prompt)

    def _generate_codi_image(self, city: str, codi_advice: str, user_id: str, condition: str = "Clear") -> Optional[str]:
        from google import genai
        from google.genai import types
        import io

        outfit_en = self._translate_codi_to_english(city, codi_advice)

        weather_scene = {
            "Rain": "rainy day, wet streets, people with umbrellas, overcast sky",
            "Drizzle": "light rain, misty atmosphere, overcast sky",
            "Thunderstorm": "stormy weather, dark clouds, dramatic sky",
            "Snow": "snowy day, snow on the ground, winter atmosphere",
            "Clouds": "cloudy day, overcast sky, soft diffused light",
            "Mist": "misty morning, foggy atmosphere",
            "Fog": "foggy atmosphere, low visibility",
            "Clear": "sunny day, clear blue sky, bright natural lighting",
            "Haze": "hazy atmosphere, warm diffused light",
        }.get(condition, "natural lighting")

        prompt = (
            f"A stylish person wearing {outfit_en}, "
            f"standing in front of a famous landmark in {city}, "
            f"{weather_scene}, "
            f"full body fashion photo, travel photography, high quality"
        )

        client = genai.Client(api_key=self.settings.gemini_api_key)

        import time
        response = None
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model="gemini-3.1-flash-image-preview",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE", "TEXT"],
                    ),
                )
                break
            except Exception as e:
                if attempt < 2 and ("503" in str(e) or "UNAVAILABLE" in str(e) or "500" in str(e)):
                    logger.warning("Gemini image gen attempt %d failed, retrying: %s", attempt + 1, e)
                    time.sleep(3 * (attempt + 1))
                else:
                    raise

        if response is None:
            return None

        image_bytes = None
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                image_bytes = part.inline_data.data
                break

        if not image_bytes:
            logger.warning("Gemini codi image response missing image data")
            return None

        s3_key = self.file_manager.upload_file(
            user_id=user_id,
            task_id=f"codi-{uuid.uuid4().hex[:8]}",
            file_bytes=image_bytes,
            content_type="image/png",
            category="codi_recommend",
        )

        return self.file_manager.get_download_url(s3_key)

    def _get_fallback(self, avg_temp: float) -> dict:
        if avg_temp >= 30:
            return FALLBACK_TEMPLATES["hot"]
        elif avg_temp >= 20:
            return FALLBACK_TEMPLATES["warm"]
        elif avg_temp >= 10:
            return FALLBACK_TEMPLATES["cool"]
        return FALLBACK_TEMPLATES["cold"]

    async def get_size_recommendation(self, user: User, task_id: str, db: AsyncSession) -> dict:
        result = await db.execute(
            select(FittingTask).where(FittingTask.id == task_id, FittingTask.user_id == user.id)
        )
        task = result.scalar_one_or_none()
        if not task:
            raise NotFoundError("피팅 결과를 찾을 수 없습니다")

        return {
            "task_id": str(task.id),
            "recommendations": MOCK_SIZE_RECOMMENDATION,
        }

    async def get_weather_codi(self, user: User, city: str) -> dict:
        if not city.strip():
            raise ValidationError("도시명을 입력해주세요")

        weather_data = await self._fetch_weather(city)
        avg_temp = weather_data["avg_temp"] if weather_data else 20

        try:
            recommendation = self._generate_codi_with_claude(city, weather_data or {"avg_temp": avg_temp})
        except Exception as e:
            logger.warning("Bedrock codi generation failed, using fallback: %s", e)
            recommendation = self._get_fallback(avg_temp)

        image_url = None
        try:
            condition = weather_data.get("condition", "Clear") if weather_data else "Clear"
            image_url = self._generate_codi_image(
                city, recommendation["codi_advice"], str(user.id), condition=condition
            )
        except Exception as e:
            logger.warning("Codi image generation failed: %s", e)

        return {
            "city": city,
            "weather": weather_data,
            "codi_advice": recommendation["codi_advice"],
            "essential_items": recommendation["essential_items"],
            "additional_tips": recommendation["additional_tips"],
            "image_url": image_url,
        }

    async def get_dutyfree_codi(self, user: User, destination: str, arrival: str) -> dict:
        from app.data.dutyfree_products import DUTY_FREE_PRODUCTS, get_products_by_ids

        weather_data = await self._fetch_weather(destination)
        avg_temp = weather_data["avg_temp"] if weather_data else 20

        product_list = "\n".join(
            f"- ID: {p['id']}, 브랜드: {p['brand']}, 이름: {p['name']}, 카테고리: {p['category']}, 설명: {p['description']}"
            for p in DUTY_FREE_PRODUCTS
        )

        prompt = (
            f"당신은 여행 패션 스타일리스트입니다.\n"
            f"여행지: {destination}\n"
            f"도착일시: {arrival}\n"
            f"날씨 정보: 평균기온 {avg_temp:.1f}°C, 날씨 상태 {weather_data.get('condition', 'Clear') if weather_data else 'Clear'}\n\n"
            f"아래 면세점 의류 목록에서 여행지 날씨와 특성에 맞는 코디를 추천해주세요.\n"
            f"상의 1개 + 하의 1개 (또는 원피스 1개) + 아우터 1개 조합으로 추천해주세요.\n\n"
            f"면세점 의류 목록:\n{product_list}\n\n"
            f"반드시 아래 JSON 형식으로만 응답하세요 (다른 텍스트 없이):\n"
            f'{{\n'
            f'  "recommended_ids": ["선택한 상품ID1", "선택한 상품ID2", "선택한 상품ID3"],\n'
            f'  "codi_advice": "3-4문장의 구체적인 코디 추천 및 이유"\n'
            f'}}'
        )

        try:
            text = self._gemini_text(prompt)

            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text[3:]
                text = text.rsplit("```", 1)[0].strip()

            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                text = text[start:end]

            result = json.loads(text)
            recommended_items = get_products_by_ids(result["recommended_ids"])
            codi_advice = result["codi_advice"]
        except Exception as e:
            logger.warning("Dutyfree codi generation failed, using fallback: %s", e)
            recommended_items = [DUTY_FREE_PRODUCTS[4], DUTY_FREE_PRODUCTS[8], DUTY_FREE_PRODUCTS[0]]
            codi_advice = self._get_fallback(avg_temp)["codi_advice"]

        return {
            "recommended_items": recommended_items,
            "codi_advice": codi_advice,
            "weather_info": {
                "avg_temp": avg_temp,
                "condition": weather_data.get("condition", "Clear") if weather_data else "Clear",
            },
        }

    DESTINATION_ATTRACTIONS_FALLBACK = {
        "tokyo": [
            {"name": "Shibuya Crossing", "name_ko": "시부야 스크램블 교차로", "description": "세계에서 가장 붐비는 교차로", "image_keyword": "shibuya crossing tokyo"},
            {"name": "Tokyo Tower", "name_ko": "도쿄 타워", "description": "도쿄의 상징적 타워", "image_keyword": "tokyo tower"},
            {"name": "Senso-ji Temple", "name_ko": "센소지", "description": "아사쿠사의 역사적 사찰", "image_keyword": "sensoji temple tokyo"},
            {"name": "Meiji Shrine", "name_ko": "메이지 신궁", "description": "도심 속 평화로운 신사", "image_keyword": "meiji shrine tokyo"},
            {"name": "Akihabara", "name_ko": "아키하바라", "description": "전자상가와 팝컬처의 거리", "image_keyword": "akihabara tokyo"},
        ],
        "bangkok": [
            {"name": "Grand Palace", "name_ko": "왕궁", "description": "태국 왕실의 화려한 궁전", "image_keyword": "grand palace bangkok"},
            {"name": "Wat Arun", "name_ko": "왓 아룬", "description": "새벽의 사원", "image_keyword": "wat arun bangkok"},
            {"name": "Khao San Road", "name_ko": "카오산 로드", "description": "여행자의 거리", "image_keyword": "khao san road bangkok"},
            {"name": "Chatuchak Market", "name_ko": "짜뚜짝 시장", "description": "세계 최대 주말 시장", "image_keyword": "chatuchak market bangkok"},
            {"name": "Wat Pho", "name_ko": "왓 포", "description": "거대한 와불이 있는 사원", "image_keyword": "wat pho bangkok"},
        ],
        "paris": [
            {"name": "Eiffel Tower", "name_ko": "에펠탑", "description": "파리의 상징적 랜드마크", "image_keyword": "eiffel tower paris"},
            {"name": "Louvre Museum", "name_ko": "루브르 박물관", "description": "세계 최대 미술관", "image_keyword": "louvre museum paris"},
            {"name": "Champs-Élysées", "name_ko": "샹젤리제 거리", "description": "파리의 대표 거리", "image_keyword": "champs elysees paris"},
            {"name": "Montmartre", "name_ko": "몽마르뜨 언덕", "description": "예술가의 언덕", "image_keyword": "montmartre paris"},
            {"name": "Seine River", "name_ko": "센강", "description": "파리를 가로지르는 강", "image_keyword": "seine river paris"},
        ],
        "london": [
            {"name": "Big Ben", "name_ko": "빅벤", "description": "영국 국회의사당의 시계탑", "image_keyword": "big ben london"},
            {"name": "Tower Bridge", "name_ko": "타워 브리지", "description": "런던의 상징적 다리", "image_keyword": "tower bridge london"},
            {"name": "Buckingham Palace", "name_ko": "버킹엄 궁전", "description": "영국 왕실 궁전", "image_keyword": "buckingham palace london"},
            {"name": "London Eye", "name_ko": "런던 아이", "description": "템즈강변 대관람차", "image_keyword": "london eye"},
            {"name": "Hyde Park", "name_ko": "하이드 파크", "description": "런던 중심부의 대형 공원", "image_keyword": "hyde park london"},
        ],
        "new york": [
            {"name": "Times Square", "name_ko": "타임스 스퀘어", "description": "뉴욕의 화려한 중심지", "image_keyword": "times square new york"},
            {"name": "Central Park", "name_ko": "센트럴 파크", "description": "맨해튼 한가운데 거대한 공원", "image_keyword": "central park new york"},
            {"name": "Statue of Liberty", "name_ko": "자유의 여신상", "description": "미국의 상징", "image_keyword": "statue of liberty new york"},
            {"name": "Brooklyn Bridge", "name_ko": "브루클린 브리지", "description": "역사적인 현수교", "image_keyword": "brooklyn bridge new york"},
            {"name": "Empire State Building", "name_ko": "엠파이어 스테이트 빌딩", "description": "뉴욕 스카이라인의 아이콘", "image_keyword": "empire state building new york"},
        ],
        "bali": [
            {"name": "Tanah Lot Temple", "name_ko": "따나롯 사원", "description": "바다 위 절벽 사원", "image_keyword": "tanah lot temple bali"},
            {"name": "Ubud Rice Terraces", "name_ko": "우붓 라이스 테라스", "description": "초록빛 계단식 논", "image_keyword": "tegallalang rice terrace bali"},
            {"name": "Uluwatu Temple", "name_ko": "울루와뚜 사원", "description": "절벽 위 힌두 사원", "image_keyword": "uluwatu temple bali"},
            {"name": "Kuta Beach", "name_ko": "쿠타 비치", "description": "발리 대표 해변", "image_keyword": "kuta beach bali"},
            {"name": "Sacred Monkey Forest", "name_ko": "몽키 포레스트", "description": "원숭이와 고대 사원의 숲", "image_keyword": "monkey forest ubud bali"},
        ],
    }

    async def get_attractions(self, destination: str) -> dict:
        prompt = (
            f"여행지 '{destination}'의 대표 관광지 5곳을 추천해주세요.\n"
            f"가상 피팅 배경으로 사용할 곳이므로 사진 배경으로 좋은 랜드마크 위주로 추천해주세요.\n\n"
            f"반드시 아래 JSON 형식으로만 응답하세요 (다른 텍스트 없이):\n"
            f'{{\n'
            f'  "attractions": [\n'
            f'    {{"name": "영문명", "name_ko": "한글명", "description": "한줄 설명", "image_keyword": "Unsplash 검색용 영문 키워드"}},\n'
            f'    ...\n'
            f'  ]\n'
            f'}}'
        )

        try:
            text = self._gemini_text(prompt)

            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text[3:]
                text = text.rsplit("```", 1)[0].strip()

            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                text = text[start:end]

            return json.loads(text)
        except Exception as e:
            logger.warning("Attractions generation failed, using fallback: %s", e)
            fallback = self.DESTINATION_ATTRACTIONS_FALLBACK.get(
                destination,
                self.DESTINATION_ATTRACTIONS_FALLBACK["paris"],
            )
            return {"attractions": fallback}

    async def _fetch_weather(self, city: str) -> Optional[dict]:
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
                return {"avg_temp": 22, "condition": "Clear", "forecasts": [], "source": "mock"}

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

    DESTINATION_CITY_MAP = {
        "tokyo": "Tokyo,JP",
        "bangkok": "Bangkok,TH",
        "paris": "Paris,FR",
        "london": "London,GB",
        "new york": "New York,US",
        "bali": "Denpasar,ID",
    }

    async def get_weather_brief(self, destination: str, arrival: str) -> dict:
        city = self.DESTINATION_CITY_MAP.get(destination, destination.title())
        weather = await self._fetch_weather(city)
        if not weather:
            return {"temp": 22, "condition": "Clear", "description": "맑음"}

        temp = weather["avg_temp"]
        condition = weather["condition"]

        if arrival and weather.get("forecasts"):
            from datetime import datetime
            try:
                arrival_dt = datetime.fromisoformat(arrival.replace("Z", "+00:00"))
                closest = min(
                    weather["forecasts"],
                    key=lambda f: abs(datetime.strptime(f["date"], "%Y-%m-%d %H:%M:%S") - arrival_dt.replace(tzinfo=None)),
                )
                temp = closest["temp"]
                condition = closest["condition"]
            except (ValueError, TypeError):
                pass

        condition_ko_map = {
            "Clear": "맑음",
            "Clouds": "흐림",
            "Rain": "비",
            "Drizzle": "이슬비",
            "Thunderstorm": "뇌우",
            "Snow": "눈",
            "Mist": "안개",
            "Fog": "안개",
            "Haze": "연무",
        }

        return {
            "temp": round(temp, 1),
            "condition": condition,
            "description": condition_ko_map.get(condition, condition),
            "city": city,
        }
