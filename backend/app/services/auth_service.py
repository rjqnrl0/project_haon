import logging

import boto3
from botocore.exceptions import ClientError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import AuthError, ValidationError
from app.models.user import User

logger = logging.getLogger("v-suitcase.auth_service")


class AuthService:
    def __init__(self):
        settings = get_settings()
        self.client = boto3.client("cognito-idp", region_name=settings.cognito_region)
        self.pool_id = settings.cognito_pool_id
        self.client_id = settings.cognito_client_id

    async def sign_up(self, email: str, password: str, db: AsyncSession) -> User:
        existing = await db.execute(select(User).where(User.email == email))
        if existing.scalar_one_or_none():
            raise ValidationError("이미 가입된 이메일입니다")

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
        db.add(user)
        await db.flush()

        return user

    async def login(self, email: str, password: str, db: AsyncSession) -> dict:
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
        try:
            self.client.global_sign_out(AccessToken=access_token)
        except ClientError as e:
            logger.warning("Logout failed: %s", e)

    async def refresh_token(self, refresh_token: str) -> dict:
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
