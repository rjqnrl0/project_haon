import io
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta, timezone
import uuid

import pytest
from PIL import Image

from app.core.errors import NotFoundError
from app.services.share_service import ShareService


def make_test_image(width=800, height=600):
    img = Image.new("RGB", (width, height), color="red")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture
def share_service(mock_s3):
    with patch("boto3.client", return_value=mock_s3):
        service = ShareService()
    service.file_manager.s3 = mock_s3
    return service


class TestAddWatermark:
    def test_watermark_returns_jpeg(self, share_service):
        image_bytes = make_test_image()
        result = share_service._add_watermark(image_bytes)
        assert len(result) > 0
        img = Image.open(io.BytesIO(result))
        assert img.format == "JPEG"

    def test_watermark_preserves_dimensions(self, share_service):
        image_bytes = make_test_image(1024, 768)
        result = share_service._add_watermark(image_bytes)
        img = Image.open(io.BytesIO(result))
        assert img.size == (1024, 768)


class TestCreateDownload:
    @pytest.mark.asyncio
    async def test_success(self, share_service, mock_user, mock_db, mock_s3):
        image_bytes = make_test_image()
        mock_body = MagicMock()
        mock_body.read.return_value = image_bytes
        mock_s3.get_object.return_value = {"Body": mock_body}

        task = MagicMock()
        task.id = uuid.uuid4()
        task.user_id = mock_user.id
        task.status = "completed"
        task.result_file_path = "some/result.jpg"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = task
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await share_service.create_download(
            user=mock_user, source_task_id=str(task.id), db=mock_db
        )
        assert "download_url" in result
        assert "filename" in result
        assert result["filename"].endswith(".jpg")

    @pytest.mark.asyncio
    async def test_task_not_found(self, share_service, mock_user, mock_db):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(NotFoundError):
            await share_service.create_download(
                user=mock_user, source_task_id=str(uuid.uuid4()), db=mock_db
            )


class TestCreateShareLink:
    @pytest.mark.asyncio
    async def test_success(self, share_service, mock_user, mock_db, mock_s3):
        image_bytes = make_test_image()
        mock_body = MagicMock()
        mock_body.read.return_value = image_bytes
        mock_s3.get_object.return_value = {"Body": mock_body}

        task = MagicMock()
        task.id = uuid.uuid4()
        task.user_id = mock_user.id
        task.status = "completed"
        task.result_file_path = "some/result.jpg"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = task
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await share_service.create_share_link(
            user=mock_user, source_task_id=str(task.id), db=mock_db
        )
        assert "share_token" in result
        assert "share_url" in result
        assert "/share/" in result["share_url"]


class TestGetSharedImage:
    @pytest.mark.asyncio
    async def test_valid_link(self, share_service, mock_db, mock_s3):
        link = MagicMock()
        link.watermarked_path = "some/shared.jpg"
        link.expires_at = datetime.now(timezone.utc) + timedelta(days=10)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = link
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await share_service.get_shared_image(share_token="abc-123", db=mock_db)
        assert "image_url" in result

    @pytest.mark.asyncio
    async def test_expired_link(self, share_service, mock_db):
        link = MagicMock()
        link.expires_at = datetime.now(timezone.utc) - timedelta(days=1)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = link
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(NotFoundError, match="만료"):
            await share_service.get_shared_image(share_token="expired-token", db=mock_db)

    @pytest.mark.asyncio
    async def test_not_found(self, share_service, mock_db):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(NotFoundError):
            await share_service.get_shared_image(share_token="nonexistent", db=mock_db)
