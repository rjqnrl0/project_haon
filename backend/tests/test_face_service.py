from unittest.mock import patch, MagicMock, AsyncMock
import pytest

from app.core.errors import ValidationError, FileTypeInvalidError
from app.services.face_service import FaceVerificationService


@pytest.fixture
def face_service(mock_s3):
    with patch("boto3.client", return_value=mock_s3):
        service = FaceVerificationService()
    service.file_manager.s3 = mock_s3
    return service


class TestRegisterFace:
    @pytest.mark.asyncio
    async def test_register_success(self, face_service, mock_user, mock_db, mock_s3):
        result = await face_service.register_face(
            user=mock_user,
            image_bytes=b"\xff\xd8\xff\xe0" * 100,
            content_type="image/jpeg",
            db=mock_db,
        )
        assert result["registered"] is True
        assert mock_user.face_registered is True
        assert mock_user.face_s3_key is not None

    @pytest.mark.asyncio
    async def test_register_replaces_existing(self, face_service, mock_user, mock_db, mock_s3):
        mock_user.face_s3_key = "old/key.jpg"
        await face_service.register_face(
            user=mock_user,
            image_bytes=b"\xff\xd8\xff\xe0" * 100,
            content_type="image/jpeg",
            db=mock_db,
        )
        mock_s3.delete_object.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_invalid_content_type(self, face_service, mock_user, mock_db):
        with pytest.raises(FileTypeInvalidError):
            await face_service.register_face(
                user=mock_user,
                image_bytes=b"not-an-image",
                content_type="text/plain",
                db=mock_db,
            )


class TestVerifyFace:
    @pytest.mark.asyncio
    async def test_verify_always_passes_phase1(self, face_service, mock_user):
        mock_user.face_registered = True
        mock_user.face_s3_key = "face/key.jpg"
        result = await face_service.verify_face(
            user=mock_user,
            image_bytes=b"\xff\xd8\xff\xe0" * 100,
            content_type="image/jpeg",
        )
        assert result["verified"] is True
        assert result["similarity"] == 95.0

    @pytest.mark.asyncio
    async def test_verify_not_registered(self, face_service, mock_user):
        mock_user.face_registered = False
        mock_user.face_s3_key = None
        with pytest.raises(ValidationError):
            await face_service.verify_face(
                user=mock_user,
                image_bytes=b"\xff\xd8\xff\xe0",
                content_type="image/jpeg",
            )
