import io
from unittest.mock import patch, MagicMock, AsyncMock
import uuid

import pytest
from PIL import Image

from app.core.errors import ValidationError, NotFoundError
from app.services.fitting_service import FittingService


def make_test_image(width=800, height=600, fmt="JPEG"):
    img = Image.new("RGB", (width, height), color="blue")
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


@pytest.fixture
def fitting_service(mock_s3):
    with patch("boto3.client", return_value=mock_s3):
        service = FittingService()
    service.file_manager.s3 = mock_s3
    return service


class TestUploadBodyImage:
    @pytest.mark.asyncio
    async def test_success(self, fitting_service, mock_user, mock_db):
        image_bytes = make_test_image(800, 600)
        result = await fitting_service.upload_body_image(
            user=mock_user,
            image_bytes=image_bytes,
            content_type="image/jpeg",
            db=mock_db,
        )
        assert "task_id" in result
        assert result["width"] == 800
        assert result["height"] == 600
        mock_db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_minimum_dimension_check(self, fitting_service, mock_user, mock_db):
        image_bytes = make_test_image(320, 240)
        with pytest.raises(ValidationError, match="640x480"):
            await fitting_service.upload_body_image(
                user=mock_user,
                image_bytes=image_bytes,
                content_type="image/jpeg",
                db=mock_db,
            )

    @pytest.mark.asyncio
    async def test_exactly_minimum_dimensions(self, fitting_service, mock_user, mock_db):
        image_bytes = make_test_image(640, 480)
        result = await fitting_service.upload_body_image(
            user=mock_user,
            image_bytes=image_bytes,
            content_type="image/jpeg",
            db=mock_db,
        )
        assert result["width"] == 640
        assert result["height"] == 480


class TestUploadClothingImage:
    @pytest.mark.asyncio
    async def test_valid_category(self, fitting_service, mock_user, mock_db):
        image_bytes = make_test_image(400, 400)
        result = await fitting_service.upload_clothing_image(
            user=mock_user,
            image_bytes=image_bytes,
            content_type="image/jpeg",
            category="top",
            db=mock_db,
        )
        assert result["category"] == "top"
        assert "clothing_id" in result

    @pytest.mark.asyncio
    async def test_invalid_category(self, fitting_service, mock_user, mock_db):
        image_bytes = make_test_image(400, 400)
        with pytest.raises(ValidationError, match="유효하지 않은 카테고리"):
            await fitting_service.upload_clothing_image(
                user=mock_user,
                image_bytes=image_bytes,
                content_type="image/jpeg",
                category="shoes",
                db=mock_db,
            )

    @pytest.mark.asyncio
    async def test_all_valid_categories(self, fitting_service, mock_user, mock_db):
        for cat in ["top", "bottom", "dress", "outer", "accessory"]:
            image_bytes = make_test_image(400, 400)
            result = await fitting_service.upload_clothing_image(
                user=mock_user,
                image_bytes=image_bytes,
                content_type="image/jpeg",
                category=cat,
                db=mock_db,
            )
            assert result["category"] == cat


class TestExecuteFitting:
    @pytest.mark.asyncio
    async def test_task_not_found(self, fitting_service, mock_user, mock_db):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(NotFoundError):
            await fitting_service.execute_fitting(
                user=mock_user,
                body_image_id=str(uuid.uuid4()),
                clothing_ids=[],
                db=mock_db,
            )

    @pytest.mark.asyncio
    async def test_mock_returns_jpeg(self, fitting_service, mock_user, mock_db, mock_s3):
        body_bytes = make_test_image(800, 600)
        mock_body = MagicMock()
        mock_body.read.return_value = body_bytes
        mock_s3.get_object.return_value = {"Body": mock_body}

        task = MagicMock()
        task.id = uuid.uuid4()
        task.user_id = mock_user.id
        task.body_file_path = "some/body.jpg"
        task.status = "pending"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = task
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await fitting_service.execute_fitting(
            user=mock_user,
            body_image_id=str(task.id),
            clothing_ids=[],
            db=mock_db,
        )
        assert result["status"] == "completed"
        assert "result_url" in result
