"""
Dashboard Layout Model
存储管理员的仪表盘布局配置
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import AdminUser


class DashboardLayout(Base):
    """Dashboard layout configuration for admin users"""

    __tablename__ = "dashboard_layouts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    admin_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("admin_users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    layout_config: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # JSON string containing grid layout configuration
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    # Relationships
    admin_user: Mapped[AdminUser] = relationship("AdminUser", back_populates="dashboard_layout")


"""
Layout Config JSON Structure:
{
    "widgets": [
        {
            "id": "stats_users",
            "type": "stat_card",
            "visible": true,
            "x": 0,
            "y": 0,
            "w": 6,
            "h": 4
        },
        {
            "id": "chart_trends",
            "type": "line_chart",
            "visible": true,
            "x": 0,
            "y": 4,
            "w": 16,
            "h": 8
        },
        ...
    ],
    "version": 1
}

Widget Types:
- stat_card: Statistics card (users, videos, comments, views)
- line_chart: Trend line chart
- pie_chart: Pie chart for distributions
- bar_chart: Bar chart for rankings
- recent_videos: Recent videos table
- quick_actions: Quick action buttons
- system_info: System information card
"""
