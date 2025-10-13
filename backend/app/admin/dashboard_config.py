"""
Dashboard Configuration API
管理员仪表盘配置API - 支持自定义布局
"""

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.dashboard import DashboardLayout
from app.models.user import AdminUser
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


# Default layout configuration
DEFAULT_LAYOUT = {
    "widgets": [
        # Stats row
        {"id": "stats_users", "type": "stat_card", "visible": True, "x": 0, "y": 0, "w": 6, "h": 4},
        {"id": "stats_videos", "type": "stat_card", "visible": True, "x": 6, "y": 0, "w": 6, "h": 4},
        {"id": "stats_comments", "type": "stat_card", "visible": True, "x": 12, "y": 0, "w": 6, "h": 4},
        {"id": "stats_views", "type": "stat_card", "visible": True, "x": 18, "y": 0, "w": 6, "h": 4},
        # Recent videos table
        {"id": "recent_videos", "type": "table", "visible": True, "x": 0, "y": 4, "w": 24, "h": 10},
        # Charts row
        {"id": "chart_trends", "type": "line_chart", "visible": True, "x": 0, "y": 14, "w": 16, "h": 10},
        {"id": "chart_types", "type": "pie_chart", "visible": True, "x": 16, "y": 14, "w": 8, "h": 10},
        # Top videos chart
        {"id": "chart_top_videos", "type": "bar_chart", "visible": True, "x": 0, "y": 24, "w": 24, "h": 10},
        # Bottom row
        {"id": "quick_actions", "type": "actions", "visible": True, "x": 0, "y": 34, "w": 12, "h": 12},
        {"id": "system_info", "type": "info", "visible": True, "x": 12, "y": 34, "w": 12, "h": 12},
    ],
    "version": 1,
}


# Schemas
class DashboardLayoutRequest(BaseModel):
    """Dashboard layout configuration request"""

    layout_config: dict


class DashboardLayoutResponse(BaseModel):
    """Dashboard layout configuration response"""

    layout_config: dict

    class Config:
        from_attributes = True


@router.get("/layout", response_model=DashboardLayoutResponse)
async def get_dashboard_layout(
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取当前管理员的仪表盘布局配置

    如果未设置，返回默认布局
    """
    # Query existing layout
    query = select(DashboardLayout).where(DashboardLayout.admin_user_id == current_admin.id)
    result = await db.execute(query)
    layout = result.scalar_one_or_none()

    if layout:
        try:
            layout_config = json.loads(layout.layout_config)
        except json.JSONDecodeError:
            layout_config = DEFAULT_LAYOUT
    else:
        layout_config = DEFAULT_LAYOUT

    return DashboardLayoutResponse(layout_config=layout_config)


@router.put("/layout", response_model=DashboardLayoutResponse)
async def save_dashboard_layout(
    request: DashboardLayoutRequest,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    保存当前管理员的仪表盘布局配置

    - **layout_config**: 布局配置对象
    """
    # Validate layout config
    if not isinstance(request.layout_config, dict):
        raise HTTPException(status_code=400, detail="Invalid layout configuration")

    if "widgets" not in request.layout_config:
        raise HTTPException(status_code=400, detail="Layout must contain 'widgets' array")

    # Convert to JSON string
    layout_json = json.dumps(request.layout_config)

    # Check if layout exists
    query = select(DashboardLayout).where(DashboardLayout.admin_user_id == current_admin.id)
    result = await db.execute(query)
    layout = result.scalar_one_or_none()

    if layout:
        # Update existing layout
        layout.layout_config = layout_json
    else:
        # Create new layout
        layout = DashboardLayout(admin_user_id=current_admin.id, layout_config=layout_json)
        db.add(layout)

    await db.commit()
    await db.refresh(layout)

    return DashboardLayoutResponse(layout_config=request.layout_config)


@router.post("/reset", response_model=DashboardLayoutResponse)
async def reset_dashboard_layout(
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    重置仪表盘布局为默认配置
    """
    # Delete existing layout
    query = select(DashboardLayout).where(DashboardLayout.admin_user_id == current_admin.id)
    result = await db.execute(query)
    layout = result.scalar_one_or_none()

    if layout:
        await db.delete(layout)
        await db.commit()

    return DashboardLayoutResponse(layout_config=DEFAULT_LAYOUT)


@router.get("/widgets")
async def get_available_widgets():
    """
    获取所有可用的组件类型及其配置

    用于前端渲染组件选择器
    """
    return {
        "widgets": [
            {
                "id": "stats_users",
                "type": "stat_card",
                "name": "Total Users",
                "name_zh": "总用户数",
                "icon": "UserOutlined",
                "minW": 4,
                "minH": 4,
                "defaultW": 6,
                "defaultH": 4,
            },
            {
                "id": "stats_videos",
                "type": "stat_card",
                "name": "Total Videos",
                "name_zh": "总视频数",
                "icon": "VideoCameraOutlined",
                "minW": 4,
                "minH": 4,
                "defaultW": 6,
                "defaultH": 4,
            },
            {
                "id": "stats_comments",
                "type": "stat_card",
                "name": "Total Comments",
                "name_zh": "总评论数",
                "icon": "CommentOutlined",
                "minW": 4,
                "minH": 4,
                "defaultW": 6,
                "defaultH": 4,
            },
            {
                "id": "stats_views",
                "type": "stat_card",
                "name": "Total Views",
                "name_zh": "总播放量",
                "icon": "EyeOutlined",
                "minW": 4,
                "minH": 4,
                "defaultW": 6,
                "defaultH": 4,
            },
            {
                "id": "recent_videos",
                "type": "table",
                "name": "Recent Videos",
                "name_zh": "最近视频",
                "icon": "FileTextOutlined",
                "minW": 12,
                "minH": 8,
                "defaultW": 24,
                "defaultH": 10,
            },
            {
                "id": "chart_trends",
                "type": "line_chart",
                "name": "Data Trends (30 days)",
                "name_zh": "数据趋势（近30天）",
                "icon": "LineChartOutlined",
                "minW": 12,
                "minH": 8,
                "defaultW": 16,
                "defaultH": 10,
            },
            {
                "id": "chart_types",
                "type": "pie_chart",
                "name": "Video Types Distribution",
                "name_zh": "视频类型分布",
                "icon": "PieChartOutlined",
                "minW": 6,
                "minH": 8,
                "defaultW": 8,
                "defaultH": 10,
            },
            {
                "id": "chart_top_videos",
                "type": "bar_chart",
                "name": "Top 10 Videos",
                "name_zh": "热门视频 TOP 10",
                "icon": "BarChartOutlined",
                "minW": 12,
                "minH": 8,
                "defaultW": 24,
                "defaultH": 10,
            },
            {
                "id": "quick_actions",
                "type": "actions",
                "name": "Quick Actions",
                "name_zh": "快捷操作",
                "icon": "ThunderboltOutlined",
                "minW": 8,
                "minH": 8,
                "defaultW": 12,
                "defaultH": 12,
            },
            {
                "id": "system_info",
                "type": "info",
                "name": "System Information",
                "name_zh": "系统信息",
                "icon": "InfoCircleOutlined",
                "minW": 8,
                "minH": 8,
                "defaultW": 12,
                "defaultH": 12,
            },
        ]
    }
