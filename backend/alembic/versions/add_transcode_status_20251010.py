"""add transcode status fields

Revision ID: add_transcode_status_20251010
Revises: add_av1_support_20251010
Create Date: 2025-10-10 07:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_transcode_status_20251010'
down_revision = 'add_av1_support_20251010'
branch_labels = None
depends_on = None


def upgrade():
    # 添加转码状态相关字段
    op.add_column('videos', sa.Column('transcode_status', sa.String(50), nullable=True, comment='转码状态: pending, processing, completed, failed'))
    op.add_column('videos', sa.Column('transcode_progress', sa.Integer, default=0, comment='转码进度 0-100'))
    op.add_column('videos', sa.Column('transcode_error', sa.Text, nullable=True, comment='转码错误信息'))
    op.add_column('videos', sa.Column('h264_transcode_at', sa.DateTime(timezone=True), nullable=True, comment='H.264转码完成时间'))
    op.add_column('videos', sa.Column('av1_transcode_at', sa.DateTime(timezone=True), nullable=True, comment='AV1转码完成时间'))

    # 添加索引
    op.create_index('idx_videos_transcode_status', 'videos', ['transcode_status'])


def downgrade():
    # 删除索引
    op.drop_index('idx_videos_transcode_status', table_name='videos')

    # 删除字段
    op.drop_column('videos', 'av1_transcode_at')
    op.drop_column('videos', 'h264_transcode_at')
    op.drop_column('videos', 'transcode_error')
    op.drop_column('videos', 'transcode_progress')
    op.drop_column('videos', 'transcode_status')
