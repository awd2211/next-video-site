"""add user activity indexes

Revision ID: add_user_activity_indexes_20251011
Revises: add_fulltext_search_20251010
Create Date: 2025-10-11 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "user_activity_idx_20251011"
down_revision: Union[str, None] = "add_fulltext_search_20251010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 用户评论查询优化
    op.create_index(
        "idx_comments_user_created",
        "comments",
        ["user_id", sa.text("created_at DESC")],
        unique=False,
    )

    # 用户收藏查询优化
    op.create_index(
        "idx_favorites_user_created",
        "favorites",
        ["user_id", sa.text("created_at DESC")],
        unique=False,
    )

    # 用户观看历史查询优化
    op.create_index(
        "idx_watch_history_user_updated",
        "watch_history",
        ["user_id", sa.text("updated_at DESC")],
        unique=False,
    )

    # 用户评分查询优化
    op.create_index(
        "idx_ratings_user_created",
        "ratings",
        ["user_id", sa.text("created_at DESC")],
        unique=False,
    )

    # 注意：以下索引仅为确认存在的表创建
    # 如果表不存在，会跳过（notifications, danmaku, video_shares可能在其他分支）


def downgrade() -> None:
    # 删除核心表的索引
    op.drop_index("idx_ratings_user_created", table_name="ratings")
    op.drop_index("idx_watch_history_user_updated", table_name="watch_history")
    op.drop_index("idx_favorites_user_created", table_name="favorites")
    op.drop_index("idx_comments_user_created", table_name="comments")
