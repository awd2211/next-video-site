"""add AV1 support to videos table

Revision ID: add_av1_support_20251010
Revises: 99205e9e5f56
Create Date: 2025-10-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_av1_support_20251010'
down_revision = '99205e9e5f56'
branch_labels = None
depends_on = None


def upgrade():
    """添加AV1支持字段到videos表"""

    # 添加AV1相关字段
    op.add_column('videos', sa.Column('av1_master_url', sa.Text(), nullable=True,
                                     comment='AV1 HLS master playlist URL'))
    op.add_column('videos', sa.Column('av1_resolutions', postgresql.JSONB(), nullable=True,
                                     server_default='{}',
                                     comment='AV1分辨率URL映射: {"1080p": "url", ...}'))
    op.add_column('videos', sa.Column('is_av1_available', sa.Boolean(), nullable=True,
                                     server_default='false',
                                     comment='是否有AV1版本可用'))
    op.add_column('videos', sa.Column('av1_file_size', sa.BigInteger(), nullable=True,
                                     comment='AV1文件总大小(字节)'))
    op.add_column('videos', sa.Column('h264_file_size', sa.BigInteger(), nullable=True,
                                     comment='H.264文件总大小(字节),用于对比'))

    # 创建索引
    op.create_index('idx_videos_av1_available', 'videos', ['is_av1_available'])

    # 更新现有记录的默认值
    op.execute("UPDATE videos SET is_av1_available = false WHERE is_av1_available IS NULL")
    op.execute("UPDATE videos SET av1_resolutions = '{}' WHERE av1_resolutions IS NULL")


def downgrade():
    """回滚AV1支持"""

    # 删除索引
    op.drop_index('idx_videos_av1_available', table_name='videos')

    # 删除字段
    op.drop_column('videos', 'h264_file_size')
    op.drop_column('videos', 'av1_file_size')
    op.drop_column('videos', 'is_av1_available')
    op.drop_column('videos', 'av1_resolutions')
    op.drop_column('videos', 'av1_master_url')
