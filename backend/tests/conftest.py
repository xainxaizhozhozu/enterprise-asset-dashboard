import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi import FastAPI
import tempfile
import os
from datetime import datetime, timezone

# Set SECRET_KEY before importing any modules that depend on it
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-32-chars-minimum"

from database import Base, get_session
from models import User
from services.auth_helper import create_access_token
from routers.auth import router as auth_router, hash_password


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Create a temporary test database and yield session factory"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    engine = create_async_engine(f"sqlite+aiosqlite:///{path}", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    yield session_factory
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()
    os.unlink(path)


@pytest_asyncio.fixture(scope="function")
async def test_app(test_db):
    """Create a test FastAPI app with dependency overrides"""
    app = FastAPI()
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
    
    async def override_get_session():
        async with test_db() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    app.dependency_overrides[get_session] = override_get_session
    
    yield app
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(test_app):
    """Create an async HTTP client for testing"""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def create_test_user(test_db):
    """Factory fixture to create test users with different roles"""
    async def _create_user(
        username: str = "testuser",
        email: str = "test@example.com",
        password: str = "password123",
        role: str = "viewer",
        is_active: int = 1
    ) -> User:
        async with test_db() as session:
            user = User(
                username=username,
                email=email,
                hashed_password=hash_password(password),
                role=role,
                is_active=is_active,
                created_at=datetime.now(timezone.utc),
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
    
    return _create_user


@pytest_asyncio.fixture
async def admin_user(create_test_user):
    """Create an admin user"""
    return await create_test_user(
        username="admin",
        email="admin@example.com",
        role="admin"
    )


@pytest_asyncio.fixture
async def manager_user(create_test_user):
    """Create a manager user"""
    return await create_test_user(
        username="manager",
        email="manager@example.com",
        role="manager"
    )


@pytest_asyncio.fixture
async def viewer_user(create_test_user):
    """Create a viewer user"""
    return await create_test_user(
        username="viewer",
        email="viewer@example.com",
        role="viewer"
    )


@pytest_asyncio.fixture
async def disabled_user(create_test_user):
    """Create a disabled user"""
    return await create_test_user(
        username="disabled",
        email="disabled@example.com",
        role="viewer",
        is_active=0
    )


@pytest.fixture
def get_token():
    """Helper to generate JWT tokens for test users"""
    def _get_token(user: User) -> str:
        return create_access_token(data={"sub": str(user.id), "role": user.role})
    return _get_token
