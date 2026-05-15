import os
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

import pytest

os.environ.update({
    "ENV": "local",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_NAME": "test",
    "DB_USERNAME": "test",
    "DB_PASSWORD": "test",
    "COGNITO_POOL_ID": "test-pool",
    "COGNITO_CLIENT_ID": "test-client",
    "COGNITO_CLIENT_SECRET": "test-secret",
    "S3_TEMP_BUCKET": "test-bucket",
    "S3_REGION": "ap-northeast-2",
    "OPENWEATHERMAP_API_KEY": "",
    "UNSPLASH_ACCESS_KEY": "",
})

from app.core.config import get_settings, Settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.flush = AsyncMock()
    db.add = MagicMock()
    return db


@pytest.fixture
def mock_user():
    from app.models.user import User
    user = MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.email = "test@example.com"
    user.face_registered = False
    user.face_s3_key = None
    return user


@pytest.fixture
def mock_s3():
    with patch("boto3.client") as mock_client:
        s3 = MagicMock()
        mock_client.return_value = s3
        s3.put_object = MagicMock()
        s3.get_object = MagicMock()
        s3.delete_object = MagicMock()
        s3.head_object = MagicMock()
        s3.generate_presigned_url = MagicMock(return_value="https://s3.example.com/test")
        yield s3
