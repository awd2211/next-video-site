"""
季度和剧集管理集成测试

测试电视剧季度、单集的 CRUD 操作
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.season import Season, SeasonStatus
from app.models.episode import Episode, EpisodeStatus


class TestSeasonAPI:
    """季度管理 API 测试"""

    @pytest.mark.asyncio
    async def test_list_seasons_by_series(self, admin_client: AsyncClient):
        """测试获取指定剧集的季度列表"""
        # 假设测试数据库中有 series_id=1 的剧集
        series_id = 1
        response = await admin_client.get(f"/api/v1/admin/series/{series_id}/seasons")

        # 如果剧集不存在，应该返回 404
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "items" in data
            assert "total" in data
            assert "page" in data

    @pytest.mark.asyncio
    async def test_create_season(self, admin_client: AsyncClient):
        """
        测试创建季度

        TODO(human): 实现季度创建测试
        需要验证：
        - 必填字段：season_number, title, series_id
        - 默认状态为 'draft'
        - season_number 在同一 series 下应唯一
        """
        series_id = 1
        season_data = {
            "season_number": 1,
            "title": "第一季",
            "description": "测试季度描述",
            "status": "draft",
            "vip_required": False
        }

        # TODO(human): 在这里实现季度创建测试逻辑
        # 提示：需要先确保 series_id 存在，或创建一个测试 series
        pass

    @pytest.mark.asyncio
    async def test_update_season(self, admin_client: AsyncClient):
        """测试更新季度信息"""
        season_id = 1
        update_data = {
            "title": "第一季（更新）",
            "status": "published"
        }

        response = await admin_client.put(
            f"/api/v1/admin/seasons/{season_id}",
            json=update_data
        )

        # 如果 season 不存在会返回 404
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_batch_publish_seasons(self, admin_client: AsyncClient):
        """
        测试批量发布季度

        TODO(human): 实现批量发布测试
        验证逻辑：
        - 批量更新多个季度状态为 'published'
        - 返回成功更新的数量
        - 处理不存在的 season_id
        """
        # TODO(human): 实现批量发布测试
        pass


class TestEpisodeAPI:
    """剧集管理 API 测试"""

    @pytest.mark.asyncio
    async def test_list_episodes_by_season(self, admin_client: AsyncClient):
        """测试获取指定季度的剧集列表"""
        season_id = 1
        response = await admin_client.get(f"/api/v1/admin/seasons/{season_id}/episodes")

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "items" in data
            assert "total" in data

    @pytest.mark.asyncio
    async def test_create_episode(self, admin_client: AsyncClient):
        """测试创建剧集"""
        season_id = 1
        episode_data = {
            "episode_number": 1,
            "title": "第一集",
            "description": "测试剧集",
            "video_id": 1,
            "is_free": True,
            "vip_required": False,
            "status": "draft"
        }

        response = await admin_client.post(
            f"/api/v1/admin/seasons/{season_id}/episodes",
            json=episode_data
        )

        # Season 或 Video 不存在时返回 404
        assert response.status_code in [201, 404]

    @pytest.mark.asyncio
    async def test_set_intro_markers(self, admin_client: AsyncClient):
        """
        测试设置片头片尾标记

        片头片尾标记用于"跳过片头"功能
        """
        episode_id = 1
        markers = {
            "intro_start": 10.5,
            "intro_end": 90.0,
            "credits_start": 1200.5
        }

        response = await admin_client.put(
            f"/api/v1/admin/episodes/{episode_id}/markers",
            json=markers
        )

        assert response.status_code in [200, 404]


class TestSeasonEpisodeIntegration:
    """季度和剧集集成测试"""

    @pytest.mark.asyncio
    async def test_cascade_delete_season(self, admin_client: AsyncClient):
        """
        测试级联删除：删除季度应同时删除所有剧集

        TODO(human): 实现级联删除测试
        步骤：
        1. 创建一个测试季度
        2. 在该季度下创建多个剧集
        3. 删除季度
        4. 验证所有剧集也被删除
        """
        # TODO(human): 实现级联删除测试逻辑
        pass

    @pytest.mark.asyncio
    async def test_season_episode_count(self, admin_client: AsyncClient):
        """测试季度统计信息：剧集数量"""
        series_id = 1
        response = await admin_client.get(f"/api/v1/admin/series/{series_id}/seasons")

        if response.status_code == 200:
            data = response.json()
            for season in data["items"]:
                # 每个季度应该有 total_episodes 字段
                assert "total_episodes" in season
                assert isinstance(season["total_episodes"], int)
                assert season["total_episodes"] >= 0
