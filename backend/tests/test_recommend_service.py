from unittest.mock import patch, MagicMock, AsyncMock
import uuid

import pytest

from app.core.errors import ValidationError, NotFoundError
from app.services.recommend_service import RecommendService, MOCK_SIZE_RECOMMENDATION


@pytest.fixture
def recommend_service():
    with patch("boto3.client"):
        service = RecommendService()
    return service


class TestGetSizeRecommendation:
    @pytest.mark.asyncio
    async def test_returns_mock_data(self, recommend_service, mock_user, mock_db):
        task = MagicMock()
        task.id = uuid.uuid4()
        task.user_id = mock_user.id

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = task
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await recommend_service.get_size_recommendation(
            user=mock_user, task_id=str(task.id), db=mock_db
        )
        assert result["recommendations"] == MOCK_SIZE_RECOMMENDATION
        assert "task_id" in result

    @pytest.mark.asyncio
    async def test_task_not_found(self, recommend_service, mock_user, mock_db):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(NotFoundError):
            await recommend_service.get_size_recommendation(
                user=mock_user, task_id=str(uuid.uuid4()), db=mock_db
            )


class TestGetWeatherCodi:
    @pytest.mark.asyncio
    async def test_empty_city_raises(self, recommend_service, mock_user):
        with pytest.raises(ValidationError, match="도시명"):
            await recommend_service.get_weather_codi(user=mock_user, city="  ")

    @pytest.mark.asyncio
    async def test_without_api_key_returns_mock(self, recommend_service, mock_user):
        result = await recommend_service.get_weather_codi(user=mock_user, city="Tokyo")
        assert result["city"] == "Tokyo"
        assert "codi_advice" in result
        assert "essential_items" in result
        assert result["weather"]["source"] == "mock"

    @pytest.mark.asyncio
    async def test_hot_template(self, recommend_service, mock_user):
        with patch.object(recommend_service, "_fetch_weather", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = {"avg_temp": 35, "condition": "Clear", "forecasts": []}
            result = await recommend_service.get_weather_codi(user=mock_user, city="Dubai")
        assert "린넨" in result["codi_advice"]
        assert "선크림" in result["essential_items"]

    @pytest.mark.asyncio
    async def test_cold_template(self, recommend_service, mock_user):
        with patch.object(recommend_service, "_fetch_weather", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = {"avg_temp": -5, "condition": "Snow", "forecasts": []}
            result = await recommend_service.get_weather_codi(user=mock_user, city="Moscow")
        assert "코트" in result["codi_advice"]
        assert "장갑" in result["essential_items"]
