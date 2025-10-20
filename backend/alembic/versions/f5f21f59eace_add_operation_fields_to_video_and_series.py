"""add_operation_fields_to_video_and_series

Revision ID: f5f21f59eace
Revises: b2725079229d
Create Date: 2025-10-20 01:49:39.626198

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5f21f59eace'
down_revision: Union[str, None] = 'b2725079229d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add operation fields to videos table
    op.add_column('videos', sa.Column('is_trending', sa.Boolean(), nullable=False, server_default='false', comment='热门标记'))
    op.add_column('videos', sa.Column('is_pinned', sa.Boolean(), nullable=False, server_default='false', comment='置顶标记'))
    op.add_column('videos', sa.Column('quality_score', sa.Integer(), nullable=False, server_default='0', comment='质量评分 0-100'))
    op.add_column('videos', sa.Column('scheduled_publish_at', sa.DateTime(timezone=True), nullable=True, comment='定时发布时间'))

    # Create indexes for videos
    op.create_index(op.f('ix_videos_is_trending'), 'videos', ['is_trending'], unique=False)
    op.create_index(op.f('ix_videos_is_pinned'), 'videos', ['is_pinned'], unique=False)
    op.create_index(op.f('ix_videos_scheduled_publish_at'), 'videos', ['scheduled_publish_at'], unique=False)

    # Add operation fields to series table
    op.add_column('series', sa.Column('is_trending', sa.Boolean(), nullable=False, server_default='false', comment='热门标记'))
    op.add_column('series', sa.Column('is_pinned', sa.Boolean(), nullable=False, server_default='false', comment='置顶标记'))
    op.add_column('series', sa.Column('quality_score', sa.Integer(), nullable=False, server_default='0', comment='质量评分 0-100'))
    op.add_column('series', sa.Column('published_at', sa.DateTime(timezone=True), nullable=True, comment='实际发布时间'))
    op.add_column('series', sa.Column('scheduled_publish_at', sa.DateTime(timezone=True), nullable=True, comment='定时发布时间'))

    # Create indexes for series
    op.create_index(op.f('ix_series_is_trending'), 'series', ['is_trending'], unique=False)
    op.create_index(op.f('ix_series_is_pinned'), 'series', ['is_pinned'], unique=False)
    op.create_index(op.f('ix_series_scheduled_publish_at'), 'series', ['scheduled_publish_at'], unique=False)


def downgrade() -> None:
    # Drop series indexes
    op.drop_index(op.f('ix_series_scheduled_publish_at'), table_name='series')
    op.drop_index(op.f('ix_series_is_pinned'), table_name='series')
    op.drop_index(op.f('ix_series_is_trending'), table_name='series')

    # Drop series columns
    op.drop_column('series', 'scheduled_publish_at')
    op.drop_column('series', 'published_at')
    op.drop_column('series', 'quality_score')
    op.drop_column('series', 'is_pinned')
    op.drop_column('series', 'is_trending')

    # Drop videos indexes
    op.drop_index(op.f('ix_videos_scheduled_publish_at'), table_name='videos')
    op.drop_index(op.f('ix_videos_is_pinned'), table_name='videos')
    op.drop_index(op.f('ix_videos_is_trending'), table_name='videos')

    # Drop videos columns
    op.drop_column('videos', 'scheduled_publish_at')
    op.drop_column('videos', 'quality_score')
    op.drop_column('videos', 'is_pinned')
    op.drop_column('videos', 'is_trending')
