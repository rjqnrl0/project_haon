from unittest.mock import patch, MagicMock
import pytest

from app.core.errors import FileTooLargeError, FileTypeInvalidError, NotFoundError
from app.services.file_manager import FileManagerService, ALLOWED_CONTENT_TYPES, MAX_FILE_SIZE


@pytest.fixture
def file_manager(mock_s3):
    with patch("boto3.client", return_value=mock_s3):
        fm = FileManagerService()
    fm.s3 = mock_s3
    return fm


class TestValidateFile:
    def test_valid_jpeg(self, file_manager):
        file_manager.validate_file("image/jpeg", 1024)

    def test_valid_png(self, file_manager):
        file_manager.validate_file("image/png", 5000)

    def test_valid_webp(self, file_manager):
        file_manager.validate_file("image/webp", 100)

    def test_invalid_content_type(self, file_manager):
        with pytest.raises(FileTypeInvalidError):
            file_manager.validate_file("text/plain", 1024)

    def test_file_too_large(self, file_manager):
        with pytest.raises(FileTooLargeError):
            file_manager.validate_file("image/jpeg", MAX_FILE_SIZE + 1)

    def test_exactly_max_size(self, file_manager):
        file_manager.validate_file("image/jpeg", MAX_FILE_SIZE)


class TestUploadFile:
    def test_upload_success(self, file_manager, mock_s3):
        result = file_manager.upload_file(
            user_id="user-1",
            task_id="task-1",
            file_bytes=b"\xff\xd8\xff\xe0",
            content_type="image/jpeg",
            category="body",
        )
        assert result.endswith(".jpg")
        assert "user-1" in result
        mock_s3.put_object.assert_called_once()

    def test_upload_png(self, file_manager, mock_s3):
        result = file_manager.upload_file(
            user_id="user-1",
            task_id="task-1",
            file_bytes=b"\x89PNG",
            content_type="image/png",
            category="clothing_top",
        )
        assert result.endswith(".png")


class TestGetDownloadUrl:
    def test_success(self, file_manager, mock_s3):
        url = file_manager.get_download_url("some/key.jpg")
        assert url == "https://s3.example.com/test"
        mock_s3.head_object.assert_called_once()

    def test_file_not_found(self, file_manager, mock_s3):
        from botocore.exceptions import ClientError
        mock_s3.head_object.side_effect = ClientError(
            {"Error": {"Code": "404"}}, "HeadObject"
        )
        with pytest.raises(NotFoundError):
            file_manager.get_download_url("missing/key.jpg")


class TestDeleteFile:
    def test_delete_success(self, file_manager, mock_s3):
        file_manager.delete_file("some/key.jpg")
        mock_s3.delete_object.assert_called_once()


class TestGetFileBytes:
    def test_success(self, file_manager, mock_s3):
        mock_body = MagicMock()
        mock_body.read.return_value = b"image-data"
        mock_s3.get_object.return_value = {"Body": mock_body}
        result = file_manager.get_file_bytes("some/key.jpg")
        assert result == b"image-data"

    def test_not_found(self, file_manager, mock_s3):
        from botocore.exceptions import ClientError
        mock_s3.get_object.side_effect = ClientError(
            {"Error": {"Code": "NoSuchKey"}}, "GetObject"
        )
        with pytest.raises(NotFoundError):
            file_manager.get_file_bytes("missing/key.jpg")
