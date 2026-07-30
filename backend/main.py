import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

load_dotenv()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from database import init_db, async_session
    from seed_data import seed_all

    await init_db()
    async with async_session() as session:
        await seed_all(session)
    logger.info("database seeded, app ready")

    yield

    logger.info("shutting down...")


app = FastAPI(
    title="Enterprise Asset & Permission Dashboard",
    version="1.0.0",
    lifespan=lifespan,
)

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "请求过于频繁，请稍后再试"})


@app.middleware("http")
async def catch_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(
            "Unhandled exception on %s %s: %s",
            request.method,
            request.url.path,
            e,
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "服务器内部错误"},
        )


@app.get("/")
async def root():
    return {"message": "Enterprise Asset & Permission Dashboard API", "version": "1.0.0"}


@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


def _register_routers():
    from routers.auth import router as auth_router
    from routers.assets import router as assets_router
    from routers.audit import router as audit_router
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
    app.include_router(assets_router, prefix="/api/v1/assets", tags=["Assets"])
    app.include_router(audit_router, prefix="/api/v1/audit", tags=["Audit"])


_register_routers()
