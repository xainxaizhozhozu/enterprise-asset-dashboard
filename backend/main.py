import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

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


@app.get("/")
async def root():
    return {"message": "Enterprise Asset & Permission Dashboard API", "version": "1.0.0"}


@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}


def _register_routers():
    from routers.auth import router as auth_router
    from routers.assets import router as assets_router
    from routers.audit import router as audit_router
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
    app.include_router(assets_router, prefix="/api/v1/assets", tags=["Assets"])
    app.include_router(audit_router, prefix="/api/v1/audit", tags=["Audit"])


_register_routers()
