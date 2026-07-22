from datetime import datetime, timezone
import re
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models import User
from services.auth_helper import create_access_token, decode_access_token

router = APIRouter()
security = HTTPBearer()


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def validate_password(password: str) -> None:
    if len(password) < 6:
        raise ValueError("密码至少 6 位")


def validate_email(email: str) -> None:
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(pattern, email):
        raise ValueError("邮箱格式不正确")


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest, session: AsyncSession = Depends(get_session)):
    try:
        validate_password(req.password)
        validate_email(req.email)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    for field in ["username", "email"]:
        result = await session.execute(select(User).where(getattr(User, field) == getattr(req, field)))
        if result.scalars().first():
            raise HTTPException(status_code=409, detail=f"{field} 已被占用")

    user = User(
        username=req.username,
        email=req.email,
        hashed_password=hash_password(req.password),
        role="viewer",
        is_active=1,
        created_at=datetime.now(timezone.utc),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return TokenResponse(access_token=token, user={
        "id": user.id, "username": user.username, "role": user.role, "email": user.email,
    })


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.username == req.username))
    user = result.scalars().first()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="账户已被禁用")

    user.last_login = datetime.now(timezone.utc)
    await session.commit()

    token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return TokenResponse(access_token=token, user={
        "id": user.id, "username": user.username, "role": user.role, "email": user.email,
    })


@router.get("/me")
async def get_current_user(token: str = Depends(security), session: AsyncSession = Depends(get_session)):
    try:
        payload = decode_access_token(token.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="无效的认证令牌")

    uid = payload.get("sub")
    if not uid:
        raise HTTPException(status_code=401, detail="无效的认证令牌")

    result = await session.execute(select(User).where(User.id == int(uid)))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return {"id": user.id, "username": user.username, "role": user.role, "email": user.email}