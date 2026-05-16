import hashlib
import logging
import uuid

import boto3
from botocore.exceptions import ClientError
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import AuthError, ValidationError
from app.models.user import User

logger = logging.getLogger("v-suitcase.auth_service")

LOCAL_JWT_SECRET = "local-dev-secret-key"
LOCAL_JWT_ALGORITHM = "HS256"

def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _create_local_token(sub: str, email: str, token_type: str = "access") -> str:
    payload = {"sub": sub, "email": email, "token_use": token_type}
    return jwt.encode(payload, LOCAL_JWT_SECRET, algorithm=LOCAL_JWT_ALGORITHM)


class AuthService:
    def __init__(self):
        settings = get_settings()
        self.is_local = settings.env == "local"
        if not self.is_local:
            self.client = boto3.client("cognito-idp", region_name=settings.cognito_region)
            self.pool_id = settings.cognito_pool_id
            self.client_id = settings.cognito_client_id

    async def sign_up(self, email: str, password: str, db: AsyncSession) -> User:
        existing = await db.execute(select(User).where(User.email == email))
        if existing.scalar_one_or_none():
            raise ValidationError("이미 가입된 이메일입니다")

        if self.is_local:
            cognito_sub = str(uuid.uuid4())
        else:
            try:
                response = self.client.sign_up(
                    ClientId=self.client_id,
                    Username=email,
                    Password=password,
                    UserAttributes=[{"Name": "email", "Value": email}],
                )
            except ClientError as e:
                code = e.response["Error"]["Code"]
                if code == "UsernameExistsException":
                    raise ValidationError("이미 가입된 이메일입니다")
                if code == "InvalidPasswordException":
                    raise ValidationError("비밀번호 형식이 올바르지 않습니다 (8자 이상, 영문+숫자+특수문자)")
                raise AuthError(detail=f"회원가입 실패: {e.response['Error']['Message']}")
            cognito_sub = response["UserSub"]

        user = User(email=email, cognito_sub=cognito_sub, face_registered=False)
        if self.is_local:
            user.password_hash = _hash_password(password)
        db.add(user)
        await db.flush()

        return user

    async def login(self, email: str, password: str, db: AsyncSession) -> dict:
        if self.is_local:
            user_result = await db.execute(select(User).where(User.email == email))
            user = user_result.scalar_one_or_none()
            if not user:
                raise AuthError(detail="이메일 또는 비밀번호가 올바르지 않습니다", code="AUTH_INVALID")

            if not user.password_hash or user.password_hash != _hash_password(password):
                raise AuthError(detail="이메일 또는 비밀번호가 올바르지 않습니다", code="AUTH_INVALID")

            access_token = _create_local_token(user.cognito_sub, email, "access")
            id_token = _create_local_token(user.cognito_sub, email, "id")
            refresh_token = _create_local_token(user.cognito_sub, email, "refresh")

            return {
                "access_token": access_token,
                "id_token": id_token,
                "refresh_token": refresh_token,
                "user": {
                    "id": str(user.id),
                    "email": email,
                    "face_registered": user.face_registered,
                },
            }

        try:
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={"USERNAME": email, "PASSWORD": password},
            )
        except ClientError as e:
            code = e.response["Error"]["Code"]
            if code in ("NotAuthorizedException", "UserNotFoundException"):
                raise AuthError(
                    detail="이메일 또는 비밀번호가 올바르지 않습니다",
                    code="AUTH_INVALID",
                )
            raise AuthError(detail="로그인 실패")

        result = response["AuthenticationResult"]

        user_result = await db.execute(select(User).where(User.email == email))
        user = user_result.scalar_one_or_none()

        return {
            "access_token": result["AccessToken"],
            "id_token": result["IdToken"],
            "refresh_token": result["RefreshToken"],
            "user": {
                "id": str(user.id) if user else None,
                "email": email,
                "face_registered": user.face_registered if user else False,
            },
        }

    async def logout(self, access_token: str) -> None:
        if self.is_local:
            return
        try:
            self.client.global_sign_out(AccessToken=access_token)
        except ClientError as e:
            logger.warning("Logout failed: %s", e)

    async def refresh_token(self, refresh_token: str) -> dict:
        if self.is_local:
            try:
                payload = jwt.decode(refresh_token, LOCAL_JWT_SECRET, algorithms=[LOCAL_JWT_ALGORITHM])
            except Exception:
                raise AuthError(detail="토큰 갱신 실패. 다시 로그인해주세요")
            return {
                "access_token": _create_local_token(payload["sub"], payload["email"], "access"),
                "id_token": _create_local_token(payload["sub"], payload["email"], "id"),
            }

        try:
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow="REFRESH_TOKEN_AUTH",
                AuthParameters={"REFRESH_TOKEN": refresh_token},
            )
        except ClientError:
            raise AuthError(detail="토큰 갱신 실패. 다시 로그인해주세요")

        result = response["AuthenticationResult"]
        return {
            "access_token": result["AccessToken"],
            "id_token": result["IdToken"],
        }
