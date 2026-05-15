import os
import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from jose import jwt
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

os.environ.update({
    "ENV": "local",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_NAME": "vsuitcase",
    "DB_USERNAME": "postgres",
    "DB_PASSWORD": "postgres",
    "COGNITO_POOL_ID": "test-pool",
    "COGNITO_CLIENT_ID": "test-client",
    "COGNITO_CLIENT_SECRET": "",
    "S3_TEMP_BUCKET": "v-suitcase-temp-local",
    "S3_REGION": "ap-northeast-2",
    "OPENWEATHERMAP_API_KEY": "",
    "UNSPLASH_ACCESS_KEY": "",
})

from app.core.config import get_settings, Settings


@pytest.fixture(autouse=True, scope="session")
def clear_settings():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest_asyncio.fixture(scope="session")
async def engine():
    settings = get_settings()
    eng = create_async_engine(settings.database_url, echo=False)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture(scope="session")
async def setup_db(engine):
    from app.models.base import Base
    from app.models.user import User
    from app.models.fitting_task import FittingTask
    from app.models.share_link import ShareLink
    from app.models.weather_request import WeatherRequest
    from app.models.size_recommendation import SizeRecommendation

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(engine, setup_db):
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def test_user(db_session):
    from app.models.user import User
    user = User(
        email=f"test-{uuid.uuid4().hex[:8]}@test.com",
        cognito_sub=str(uuid.uuid4()),
        face_registered=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


def make_token(cognito_sub: str) -> str:
    return jwt.encode({"sub": cognito_sub, "email": "test@test.com"}, "fake-key", algorithm="HS256")


@pytest.fixture
def auth_headers(test_user):
    token = make_token(str(test_user.cognito_sub))
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def client(setup_db):
    from app.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
