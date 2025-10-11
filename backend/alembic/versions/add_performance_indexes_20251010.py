"""add additional performance indexes

Revision ID: add_performance_indexes_20251010
Revises: add_comment_likes_table_20251010
Create Date: 2025-10-10 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_performance_indexes_20251010'
down_revision: Union[str, None] = 'add_comment_likes_table_20251010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 视频查询优化索引
    
    # 1. 热门视频查询（按浏览量排序）
    op.create_index(
        'idx_videos_status_view_count',
        'videos',
        ['status', sa.text('view_count DESC')],
        unique=False
    )
    
    # 2. 高分视频查询（按评分排序）
    op.create_index(
        'idx_videos_status_rating',
        'videos',
        ['status', sa.text('average_rating DESC')],
        unique=False
    )
    
    # 3. 精选视频查询
    op.create_index(
        'idx_videos_status_featured_order',
        'videos',
        ['status', 'is_featured', sa.text('sort_order DESC')],
        unique=False
    )
    
    # 4. 推荐视频查询
    op.create_index(
        'idx_videos_status_recommended_order',
        'videos',
        ['status', 'is_recommended', sa.text('sort_order DESC')],
        unique=False
    )
    
    # 5. 按国家和年份筛选
    op.create_index(
        'idx_videos_country_year_status',
        'videos',
        ['country_id', 'release_year', 'status'],
        unique=False
    )
    
    # 评论查询优化
    
    # 6. 评论回复查询（parent_id + status + 时间排序）
    op.create_index(
        'idx_comments_parent_status_created',
        'comments',
        ['parent_id', 'status', sa.text('created_at DESC')],
        unique=False
    )
    
    # 关联表查询优化
    
    # 7. video_categories 关联查询
    op.create_index(
        'idx_video_categories_category_video',
        'video_categories',
        ['category_id', 'video_id'],
        unique=False
    )
    
    # 8. video_tags 关联查询
    op.create_index(
        'idx_video_tags_tag_video',
        'video_tags',
        ['tag_id', 'video_id'],
        unique=False
    )
    
    # 9. video_actors 关联查询
    op.create_index(
        'idx_video_actors_actor_video',
        'video_actors',
        ['actor_id', 'video_id'],
        unique=False
    )
    
    # 10. video_directors 关联查询
    op.create_index(
        'idx_video_directors_director_video',
        'video_directors',
        ['director_id', 'video_id'],
        unique=False
    )


def downgrade() -> None:
    # 删除所有索引
    op.drop_index('idx_video_directors_director_video', table_name='video_directors')
    op.drop_index('idx_video_actors_actor_video', table_name='video_actors')
    op.drop_index('idx_video_tags_tag_video', table_name='video_tags')
    op.drop_index('idx_video_categories_category_video', table_name='video_categories')
    op.drop_index('idx_comments_parent_status_created', table_name='comments')
    op.drop_index('idx_videos_country_year_status', table_name='videos')
    op.drop_index('idx_videos_status_recommended_order', table_name='videos')
    op.drop_index('idx_videos_status_featured_order', table_name='videos')
    op.drop_index('idx_videos_status_rating', table_name='videos')
    op.drop_index('idx_videos_status_view_count', table_name='videos')


