"""add subtitles table

Revision ID: add_subtitles_20251010
Revises: add_notifications_20251010
Create Date: 2025-10-10 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_subtitles_20251010'
down_revision = 'add_notifications_20251010'
branch_labels = None
depends_on = None


def upgrade():
    # 创建subtitles表
    op.create_table(
        'subtitles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('video_id', sa.Integer(), nullable=False),
        sa.Column('language', sa.String(50), nullable=False, comment='语言代码 (zh-CN, en-US, ja, ko, etc.)'),
        sa.Column('language_name', sa.String(100), nullable=False, comment='语言名称 (简体中文, English, etc.)'),
        sa.Column('file_url', sa.String(1000), nullable=False, comment='字幕文件URL'),
        sa.Column('format', sa.String(20), nullable=False, comment='字幕格式 (srt, vtt, ass)'),
        sa.Column('is_default', sa.Boolean(), default=False, nullable=False, comment='是否默认字幕'),
        sa.Column('is_auto_generated', sa.Boolean(), default=False, nullable=False, comment='是否AI自动生成'),
        sa.Column('sort_order', sa.Integer(), default=0, comment='排序顺序'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 创建索引
    op.create_index('idx_subtitles_video_id', 'subtitles', ['video_id'])
    op.create_index('idx_subtitles_language', 'subtitles', ['language'])

    # 添加外键约束
    op.create_foreign_key(
        'fk_subtitles_video_id',
        'subtitles', 'videos',
        ['video_id'], ['id'],
        ondelete='CASCADE'
    )

    # 添加唯一约束 (同一视频不能有重复语言的字幕)
    op.create_unique_constraint(
        'uq_video_language',
        'subtitles',
        ['video_id', 'language']
    )


def downgrade():
    op.drop_table('subtitles')
