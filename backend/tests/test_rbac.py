import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI, Depends
import os

os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-32-chars-minimum"

from routers.auth import require_role, get_current_user
from database import get_session


@pytest.fixture
def rbac_app(test_app):
    """Create a FastAPI app with role-based test endpoints"""

    @test_app.get("/admin-only")
    async def admin_endpoint(user=Depends(require_role("admin"))):
        return {"message": "admin access granted"}

    @test_app.get("/manager-only")
    async def manager_endpoint(user=Depends(require_role("manager"))):
        return {"message": "manager access granted"}

    @test_app.get("/viewer-only")
    async def viewer_endpoint(user=Depends(require_role("viewer"))):
        return {"message": "viewer access granted"}

    @test_app.get("/admin-or-manager")
    async def admin_or_manager_endpoint(user=Depends(require_role("admin", "manager"))):
        return {"message": "admin or manager access granted"}

    @test_app.get("/any-role")
    async def any_role_endpoint(
        user=Depends(require_role("admin", "manager", "viewer")),
    ):
        return {"message": "any role access granted"}

    return test_app


@pytest.fixture
async def rbac_client(rbac_app):
    """Create an async HTTP client for RBAC testing"""
    transport = ASGITransport(app=rbac_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
class TestAdminRole:
    """Tests for admin role access"""

    async def test_admin_can_access_admin_endpoint(
        self, rbac_client: AsyncClient, admin_user, get_token
    ):
        """Admin should access admin-only endpoints"""
        token = get_token(admin_user)
        response = await rbac_client.get(
            "/admin-only",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["message"] == "admin access granted"

    async def test_admin_cannot_access_manager_only_endpoint(
        self, rbac_client: AsyncClient, admin_user, get_token
    ):
        """Admin should NOT access manager-only endpoints (role-specific)"""
        token = get_token(admin_user)
        response = await rbac_client.get(
            "/manager-only",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    async def test_admin_can_access_multi_role_endpoint(
        self, rbac_client: AsyncClient, admin_user, get_token
    ):
        """Admin should access endpoints accepting multiple roles including admin"""
        token = get_token(admin_user)
        response = await rbac_client.get(
            "/admin-or-manager",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200


@pytest.mark.asyncio
class TestManagerRole:
    """Tests for manager role access"""

    async def test_manager_cannot_access_admin_endpoint(
        self, rbac_client: AsyncClient, manager_user, get_token
    ):
        """Manager should NOT access admin-only endpoints"""
        token = get_token(manager_user)
        response = await rbac_client.get(
            "/admin-only",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    async def test_manager_can_access_manager_endpoint(
        self, rbac_client: AsyncClient, manager_user, get_token
    ):
        """Manager should access manager-only endpoints"""
        token = get_token(manager_user)
        response = await rbac_client.get(
            "/manager-only",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["message"] == "manager access granted"

    async def test_manager_cannot_access_viewer_endpoint(
        self, rbac_client: AsyncClient, manager_user, get_token
    ):
        """Manager should NOT access viewer-only endpoints"""
        token = get_token(manager_user)
        response = await rbac_client.get(
            "/viewer-only",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    async def test_manager_can_access_multi_role_endpoint(
        self, rbac_client: AsyncClient, manager_user, get_token
    ):
        """Manager should access endpoints accepting multiple roles including manager"""
        token = get_token(manager_user)
        response = await rbac_client.get(
            "/admin-or-manager",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200


@pytest.mark.asyncio
class TestViewerRole:
    """Tests for viewer role access"""

    async def test_viewer_cannot_access_admin_endpoint(
        self, rbac_client: AsyncClient, viewer_user, get_token
    ):
        """Viewer should NOT access admin-only endpoints"""
        token = get_token(viewer_user)
        response = await rbac_client.get(
            "/admin-only",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    async def test_viewer_cannot_access_manager_endpoint(
        self, rbac_client: AsyncClient, viewer_user, get_token
    ):
        """Viewer should NOT access manager-only endpoints"""
        token = get_token(viewer_user)
        response = await rbac_client.get(
            "/manager-only",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    async def test_viewer_can_access_viewer_endpoint(
        self, rbac_client: AsyncClient, viewer_user, get_token
    ):
        """Viewer should access viewer-only endpoints"""
        token = get_token(viewer_user)
        response = await rbac_client.get(
            "/viewer-only",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["message"] == "viewer access granted"

    async def test_viewer_can_access_any_role_endpoint(
        self, rbac_client: AsyncClient, viewer_user, get_token
    ):
        """Viewer should access endpoints accepting any role"""
        token = get_token(viewer_user)
        response = await rbac_client.get(
            "/any-role",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200


@pytest.mark.asyncio
class TestDisabledUserAccess:
    """Tests for disabled user access control"""

    async def test_disabled_user_gets_403_on_admin_endpoint(
        self, rbac_client: AsyncClient, disabled_user, get_token
    ):
        """Disabled user should get 403 even with valid token"""
        token = get_token(disabled_user)
        response = await rbac_client.get(
            "/admin-only",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    async def test_disabled_user_gets_403_on_viewer_endpoint(
        self, rbac_client: AsyncClient, disabled_user, get_token
    ):
        """Disabled user should get 403 even on viewer endpoints"""
        token = get_token(disabled_user)
        response = await rbac_client.get(
            "/viewer-only",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403


@pytest.mark.asyncio
class TestRequireRoleWithMultipleRoles:
    """Tests for require_role with multiple roles"""

    async def test_require_role_admin_or_manager_allows_admin(
        self, rbac_client: AsyncClient, admin_user, get_token
    ):
        """require_role(admin, manager) should allow admin"""
        token = get_token(admin_user)
        response = await rbac_client.get(
            "/admin-or-manager",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

    async def test_require_role_admin_or_manager_allows_manager(
        self, rbac_client: AsyncClient, manager_user, get_token
    ):
        """require_role(admin, manager) should allow manager"""
        token = get_token(manager_user)
        response = await rbac_client.get(
            "/admin-or-manager",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

    async def test_require_role_admin_or_manager_denies_viewer(
        self, rbac_client: AsyncClient, viewer_user, get_token
    ):
        """require_role(admin, manager) should deny viewer"""
        token = get_token(viewer_user)
        response = await rbac_client.get(
            "/admin-or-manager",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    async def test_require_role_any_allows_all_roles(
        self, rbac_client: AsyncClient, admin_user, manager_user, viewer_user, get_token
    ):
        """require_role with all roles should allow all active users"""
        for user in [admin_user, manager_user, viewer_user]:
            token = get_token(user)
            response = await rbac_client.get(
                "/any-role",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == 200, f"Failed for {user.role}"


@pytest.mark.asyncio
class TestAuthenticationRequirements:
    """Tests for authentication requirements in RBAC"""

    async def test_unauthenticated_request_returns_403(self, rbac_client: AsyncClient):
        """Unauthenticated request should return 403"""
        response = await rbac_client.get("/admin-only")
        assert response.status_code == 403

    async def test_invalid_token_returns_401(self, rbac_client: AsyncClient):
        """Invalid token should return 401"""
        response = await rbac_client.get(
            "/admin-only",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401
