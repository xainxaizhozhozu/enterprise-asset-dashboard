import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY 未设置！请在 .env 文件中设置一个安全的随机密钥。"
        "可用命令生成: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
    )
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = timedelta(hours=8)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + ACCESS_TOKEN_EXPIRE
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
