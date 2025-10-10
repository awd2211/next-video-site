"""add notifications table

Revision ID: add_notifications_20251010
Revises: add_transcode_status_20251010
Create Date: 2025-10-10 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = 'add_notifications_20251010'
down_revision = 'add_transcode_status_20251010'
branch_labels = None
depends_on = None


def upgrade():
    # 创建notifications表
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(50), nullable=False, comment='通知类型: comment_reply, video_published, system_announcement, etc.'),
        sa.Column('title', sa.String(200), nullable=False, comment='通知标题'),
        sa.Column('content', sa.Text(), nullable=False, comment='通知内容'),
        sa.Column('related_type', sa.String(50), nullable=True, comment='关联对象类型: video, comment, user, etc.'),
        sa.Column('related_id', sa.Integer(), nullable=True, comment='关联对象ID'),
        sa.Column('link', sa.String(500), nullable=True, comment='跳转链接'),
        sa.Column('is_read', sa.Boolean(), default=False, nullable=False, comment='是否已读'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True, comment='阅读时间'),
        sa.PrimaryKeyConstraint('id')
    )

    # 创建索引
    op.create_index('idx_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('idx_notifications_type', 'notifications', ['type'])
    op.create_index('idx_notifications_is_read', 'notifications', ['is_read'])
    op.create_index('idx_notifications_created_at', 'notifications', ['created_at'])

    # 添加外键约束
    op.create_foreign_key(
        'fk_notifications_user_id',
        'notifications', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade():
    op.drop_table('notifications')
