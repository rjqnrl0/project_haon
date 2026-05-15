from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
auth_service = AuthService()


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    email: str
    face_registered: bool


class AuthResponse(BaseModel):
    access_token: str
    id_token: str
    refresh_token: str
    user: UserResponse


@router.post("/signup", response_model=AuthResponse)
async def signup(body: SignUpRequest, db: AsyncSession = Depends(get_db)):
    user = await auth_service.sign_up(body.email, body.password, db)
    tokens = await auth_service.login(body.email, body.password, db)
    return tokens


@router.post("/login", response_model=AuthResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.login(body.email, body.password, db)


@router.post("/logout")
async def logout(request: Request, _: User = Depends(get_current_user)):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.split(" ", 1)[1] if " " in auth_header else ""
    await auth_service.logout(token)
    return {"detail": "로그아웃 완료"}


@router.post("/refresh")
async def refresh(body: RefreshRequest):
    return await auth_service.refresh_token(body.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return UserResponse(
        id=str(user.id),
        email=user.email,
        face_registered=user.face_registered,
    )
