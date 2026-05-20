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

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        })

        response = self.bedrock.invoke_model(
            modelId="us.anthropic.claude-sonnet-4-6",
            contentType="application/json",
            accept="application/json",
            body=body,
        )

        resp_body = json.loads(response["body"].read())
        text = resp_body["content"][0]["text"].strip()

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
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 200,
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        })
        response = self.bedrock.invoke_model(
            modelId="us.anthropic.claude-sonnet-4-6",
            contentType="application/json",
            accept="application/json",
            body=body,
        )
        resp_body = json.loads(response["body"].read())
        return resp_body["content"][0]["text"].strip()

    def _generate_codi_image(self, city: str, codi_advice: str, user_id: str) -> Optional[str]:
        from PIL import Image
        import io

        outfit_en = self._translate_codi_to_english(city, codi_advice)

        img = Image.new("RGB", (512, 768), (200, 200, 200))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        image_b64 = base64.b64encode(buf.getvalue()).decode()

        prompt = (
            f"A stylish person wearing {outfit_en}, "
            f"standing in front of a famous landmark in {city}, "
            f"full body fashion photo, natural lighting, travel photography, high quality"
        )

        body = json.dumps({
            "image": image_b64,
            "search_prompt": "the gray background",
            "prompt": prompt,
        })

        response = self.bedrock.invoke_model(
            modelId="us.stability.stable-image-search-replace-v1:0",
            contentType="application/json",
            accept="application/json",
            body=body,
        )

        resp_body = json.loads(response["body"].read())
        if "images" not in resp_body or not resp_body["images"]:
            logger.warning("Stability response missing images: %s", list(resp_body.keys()))
            return None
        image_bytes = base64.b64decode(resp_body["images"][0])

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
            image_url = self._generate_codi_image(
                city, recommendation["codi_advice"], str(user.id)
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

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        })

        try:
            response = self.bedrock.invoke_model(
                modelId="us.anthropic.claude-sonnet-4-6",
                contentType="application/json",
                accept="application/json",
                body=body,
            )
            resp_body = json.loads(response["body"].read())
            text = resp_body["content"][0]["text"].strip()

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

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        })

        try:
            response = self.bedrock.invoke_model(
                modelId="us.anthropic.claude-sonnet-4-6",
                contentType="application/json",
                accept="application/json",
                body=body,
            )
            resp_body = json.loads(response["body"].read())
            text = resp_body["content"][0]["text"].strip()

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
            return {
                "attractions": [
                    {"name": "Eiffel Tower", "name_ko": "에펠탑", "description": "파리의 상징적 랜드마크", "image_keyword": "eiffel tower paris"},
                    {"name": "Louvre Museum", "name_ko": "루브르 박물관", "description": "세계 최대 미술관", "image_keyword": "louvre museum paris"},
                    {"name": "Champs-Élysées", "name_ko": "샹젤리제 거리", "description": "파리의 대표 거리", "image_keyword": "champs elysees paris"},
                    {"name": "Montmartre", "name_ko": "몽마르뜨 언덕", "description": "예술가의 언덕", "image_keyword": "montmartre paris"},
                    {"name": "Seine River", "name_ko": "센강", "description": "파리를 가로지르는 강", "image_keyword": "seine river paris"},
                ]
            }

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
