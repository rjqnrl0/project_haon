import logging
from typing import Optional

import httpx
from fastapi import Depends, Request
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.errors import AuthError
from app.models.user import User

logger = logging.getLogger("v-suitcase.auth")

_jwks_cache: Optional[dict] = None


async def _get_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache:
        return _jwks_cache

    settings = get_settings()
    url = (
        f"https://cognito-idp.{settings.cognito_region}.amazonaws.com"
        f"/{settings.cognito_pool_id}/.well-known/jwks.json"
    )
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        _jwks_cache = resp.json()
    return _jwks_cache


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User:
    settings = get_settings()

    # Local dev: bypass auth entirely, return or create a dummy user
    if settings.env == "local":
        result = await db.execute(select(User).where(User.email == "local@dev.test"))
        user = result.scalar_one_or_none()
        if not user:
            user = User(email="local@dev.test", cognito_sub="local-dev-user", face_registered=True)
            db.add(user)
            await db.commit()
            await db.refresh(user)
        return user

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise AuthError()

    token = auth_header.split(" ", 1)[1]

    try:
        jwks = await _get_jwks()
        header = jwt.get_unverified_header(token)
        key = next(
            (k for k in jwks.get("keys", []) if k["kid"] == header.get("kid")),
            None,
        )
        if not key:
            raise AuthError(detail="유효하지 않은 토큰입니다", code="AUTH_INVALID")

        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=settings.cognito_client_id,
            issuer=f"https://cognito-idp.{settings.cognito_region}.amazonaws.com/{settings.cognito_pool_id}",
        )
    except JWTError:
        raise AuthError(detail="유효하지 않은 토큰입니다", code="AUTH_INVALID")

    cognito_sub = payload.get("sub")
    if not cognito_sub:
        raise AuthError(detail="유효하지 않은 토큰입니다", code="AUTH_INVALID")

    result = await db.execute(select(User).where(User.cognito_sub == cognito_sub))
    user = result.scalar_one_or_none()

    if not user:
        raise AuthError(detail="사용자를 찾을 수 없습니다", code="AUTH_INVALID")

    return user
