"""add_sentry_config_table

Revision ID: f0e62db97990
Revises: c510827f253d
Create Date: 2025-10-16 10:54:11.469130

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f0e62db97990'
down_revision: Union[str, None] = 'c510827f253d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建 sentry_config 表
    op.create_table(
        'sentry_config',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dsn', sa.String(length=500), nullable=False, comment='Sentry DSN'),
        sa.Column('environment', sa.String(length=50), nullable=True, comment='环境名称'),
        sa.Column('frontend_enabled', sa.Boolean(), nullable=True, comment='用户前端是否启用'),
        sa.Column('admin_frontend_enabled', sa.Boolean(), nullable=True, comment='管理前端是否启用'),
        sa.Column('traces_sample_rate', sa.String(length=10), nullable=True, comment='性能监控采样率'),
        sa.Column('replays_session_sample_rate', sa.String(length=10), nullable=True, comment='会话回放采样率'),
        sa.Column('replays_on_error_sample_rate', sa.String(length=10), nullable=True, comment='错误回放采样率'),
        sa.Column('ignore_errors', sa.Text(), nullable=True, comment='忽略的错误列表（JSON数组）'),
        sa.Column('allowed_urls', sa.Text(), nullable=True, comment='允许上报的URL列表（JSON数组）'),
        sa.Column('denied_urls', sa.Text(), nullable=True, comment='拒绝上报的URL列表（JSON数组）'),
        sa.Column('release_version', sa.String(length=100), nullable=True, comment='发布版本号'),
        sa.Column('debug_mode', sa.Boolean(), nullable=True, comment='调试模式'),
        sa.Column('attach_stacktrace', sa.Boolean(), nullable=True, comment='自动附加堆栈跟踪'),
        sa.Column('description', sa.Text(), nullable=True, comment='配置说明'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True, comment='创建者管理员ID'),
        sa.Column('updated_by', sa.Integer(), nullable=True, comment='更新者管理员ID'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sentry_config_id'), 'sentry_config', ['id'], unique=False)


def downgrade() -> None:
    # 删除 sentry_config 表
    op.drop_index(op.f('ix_sentry_config_id'), table_name='sentry_config')
    op.drop_table('sentry_config')
