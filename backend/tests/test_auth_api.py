import pytest
from httpx import AsyncClient
import os

os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-32-chars-minimum"


@pytest.mark.asyncio
class TestRegisterEndpoint:
    """Tests for POST /api/v1/auth/register"""

    async def test_register_success(self, client: AsyncClient):
        """Register should create a new user and return token"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == "newuser"
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["role"] == "viewer"
        assert "id" in data["user"]

    async def test_register_duplicate_username(self, client: AsyncClient, create_test_user):
        """Register with duplicate username should return 409"""
        await create_test_user(username="existinguser", email="existing@example.com")
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "existinguser",
                "email": "newemail@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 409

    async def test_register_duplicate_email(self, client: AsyncClient, create_test_user):
        """Register with duplicate email should return 409"""
        await create_test_user(username="user1", email="duplicate@example.com")
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "user2",
                "email": "duplicate@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 409

    async def test_register_short_password(self, client: AsyncClient):
        """Register with short password (< 6 chars) should return 422"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "12345",
            },
        )
        assert response.status_code == 422

    async def test_register_invalid_email(self, client: AsyncClient):
        """Register with invalid email should return 422"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "invalid-email",
                "password": "password123",
            },
        )
        assert response.status_code == 422

    async def test_register_missing_fields(self, client: AsyncClient):
        """Register with missing required fields should return 422"""
        response = await client.post(
            "/api/v1/auth/register",
            json={"username": "testuser"},
        )
        assert response.status_code == 422


@pytest.mark.asyncio
class TestLoginEndpoint:
    """Tests for POST /api/v1/auth/login"""

    async def test_login_success(self, client: AsyncClient, create_test_user):
        """Login with correct credentials should return token"""
        await create_test_user(
            username="loginuser",
            email="login@example.com",
            password="correctpassword",
        )
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "loginuser", "password": "correctpassword"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "loginuser"

    async def test_login_wrong_password(self, client: AsyncClient, create_test_user):
        """Login with wrong password should return 401"""
        await create_test_user(
            username="loginuser",
            email="login@example.com",
            password="correctpassword",
        )
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "loginuser", "password": "wrongpassword"},
        )
        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Login with non-existent user should return 401"""
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "nonexistent", "password": "password123"},
        )
        assert response.status_code == 401

    async def test_login_disabled_account(self, client: AsyncClient, disabled_user):
        """Login with disabled account should return 403"""
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": disabled_user.username, "password": "password123"},
        )
        assert response.status_code == 403


@pytest.mark.asyncio
class TestGetMeEndpoint:
    """Tests for GET /api/v1/auth/me"""

    async def test_get_me_with_valid_token(self, client: AsyncClient, admin_user, get_token):
        """Get me with valid token should return user info"""
        token = get_token(admin_user)
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == admin_user.id
        assert data["username"] == admin_user.username
        assert data["email"] == admin_user.email
        assert data["role"] == admin_user.role

    async def test_get_me_without_token(self, client: AsyncClient):
        """Get me without token should return 403"""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 403

    async def test_get_me_with_invalid_token(self, client: AsyncClient):
        """Get me with invalid token should return 401"""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401

    async def test_get_me_with_expired_token(self, client: AsyncClient):
        """Get me with expired token should return 401"""
        import jwt
        from datetime import datetime, timedelta, timezone
        from services.auth_helper import SECRET_KEY, ALGORITHM

        expired_data = {
            "sub": "1",
            "role": "admin",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        }
        expired_token = jwt.encode(expired_data, SECRET_KEY, algorithm=ALGORITHM)
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401

    async def test_get_me_disabled_user(self, client: AsyncClient, disabled_user, get_token):
        """Get me with disabled user should return 403"""
        token = get_token(disabled_user)
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403
