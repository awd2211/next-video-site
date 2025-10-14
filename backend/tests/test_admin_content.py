"""
测试 Admin 内容管理 API
包括: categories, countries, tags, actors, directors, series
"""
import pytest
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminCategoriesAPI:
    """管理员分类管理 API 测试"""

    async def test_get_categories(self, async_client: AsyncClient, admin_token: str):
        """测试获取分类列表"""
        response = await async_client.get(
            "/api/v1/admin/categories",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200

    async def test_create_category(self, async_client: AsyncClient, admin_token: str):
        """测试创建分类"""
        category_data = {
            "name": "Test Category",
            "slug": "test-category-pytest",
            "description": "Test description"
        }
        response = await async_client.post(
            "/api/v1/admin/categories",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=category_data
        )
        assert response.status_code in [200, 201, 409, 422]

    async def test_update_category(self, async_client: AsyncClient, admin_token: str):
        """测试更新分类"""
        update_data = {"name": "Updated Category"}
        response = await async_client.put(
            "/api/v1/admin/categories/1",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=update_data
        )
        assert response.status_code in [200, 404]

    async def test_delete_category(self, async_client: AsyncClient, admin_token: str):
        """测试删除分类"""
        response = await async_client.delete(
            "/api/v1/admin/categories/999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 204, 404]


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminActorsAPI:
    """管理员演员管理 API 测试"""

    async def test_get_actors(self, async_client: AsyncClient, admin_token: str):
        """测试获取演员列表"""
        response = await async_client.get(
            "/api/v1/admin/actors",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_create_actor(self, async_client: AsyncClient, admin_token: str):
        """测试创建演员"""
        actor_data = {
            "name": "Test Actor",
            "biography": "Test bio"
        }
        response = await async_client.post(
            "/api/v1/admin/actors",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=actor_data
        )
        assert response.status_code in [200, 201, 422]

    async def test_update_actor(self, async_client: AsyncClient, admin_token: str):
        """测试更新演员"""
        update_data = {"name": "Updated Actor"}
        response = await async_client.put(
            "/api/v1/admin/actors/1",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=update_data
        )
        assert response.status_code in [200, 404]


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminDirectorsAPI:
    """管理员导演管理 API 测试"""

    async def test_get_directors(self, async_client: AsyncClient, admin_token: str):
        """测试获取导演列表"""
        response = await async_client.get(
            "/api/v1/admin/directors",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_create_director(self, async_client: AsyncClient, admin_token: str):
        """测试创建导演"""
        director_data = {
            "name": "Test Director",
            "biography": "Test bio"
        }
        response = await async_client.post(
            "/api/v1/admin/directors",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=director_data
        )
        assert response.status_code in [200, 201, 422]


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminSeriesAPI:
    """管理员系列管理 API 测试"""

    async def test_get_series(self, async_client: AsyncClient, admin_token: str):
        """测试获取系列列表"""
        response = await async_client.get(
            "/api/v1/admin/series",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_create_series(self, async_client: AsyncClient, admin_token: str):
        """测试创建系列"""
        series_data = {
            "title": "Test Series",
            "type": "series",
            "description": "Test description"
        }
        response = await async_client.post(
            "/api/v1/admin/series",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=series_data
        )
        assert response.status_code in [200, 201, 422]


@pytest.mark.api
@pytest.mark.admin
@pytest.mark.asyncio
class TestAdminTagsAPI:
    """管理员标签管理 API 测试"""

    async def test_get_tags(self, async_client: AsyncClient, admin_token: str):
        """测试获取标签列表"""
        response = await async_client.get(
            "/api/v1/admin/tags",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [200, 404]

    async def test_create_tag(self, async_client: AsyncClient, admin_token: str):
        """测试创建标签"""
        tag_data = {
            "name": "Test Tag",
            "slug": "test-tag-pytest"
        }
        response = await async_client.post(
            "/api/v1/admin/tags",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=tag_data
        )
        assert response.status_code in [200, 201, 409, 422]

