"""add_ai_providers_table

Revision ID: 0e8f9139d7ca
Revises: 04ae0c4b8a16
Create Date: 2025-10-13 09:42:07.457646

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0e8f9139d7ca'
down_revision: Union[str, None] = '04ae0c4b8a16'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create AI Provider Type enum if not exists
    connection = op.get_bind()
    connection.execute(sa.text("""
        DO $$ BEGIN
            CREATE TYPE aiprovidertype AS ENUM ('openai', 'grok', 'google');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """))

    # Create ai_providers table
    op.create_table('ai_providers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False, comment='配置名称'),
    sa.Column('provider_type', postgresql.ENUM('openai', 'grok', 'google', name='aiprovidertype', create_type=False), nullable=False, comment='提供商类型'),
    sa.Column('description', sa.Text(), nullable=True, comment='配置描述'),
    sa.Column('api_key', sa.String(length=500), nullable=False, comment='API密钥(加密存储)'),
    sa.Column('base_url', sa.String(length=500), nullable=True, comment='API基础URL(可选)'),
    sa.Column('model_name', sa.String(length=100), nullable=False, comment='模型名称'),
    sa.Column('max_tokens', sa.Integer(), nullable=True, comment='最大令牌数'),
    sa.Column('temperature', sa.Float(), nullable=True, comment='温度参数'),
    sa.Column('top_p', sa.Float(), nullable=True, comment='Top P参数'),
    sa.Column('frequency_penalty', sa.Float(), nullable=True, comment='频率惩罚'),
    sa.Column('presence_penalty', sa.Float(), nullable=True, comment='存在惩罚'),
    sa.Column('settings', sa.JSON(), nullable=True, comment='额外设置(JSON)'),
    sa.Column('enabled', sa.Boolean(), nullable=False, comment='是否启用'),
    sa.Column('is_default', sa.Boolean(), nullable=False, comment='是否为默认配置'),
    sa.Column('total_requests', sa.Integer(), nullable=False, comment='总请求次数'),
    sa.Column('total_tokens', sa.Integer(), nullable=False, comment='总令牌使用量'),
    sa.Column('last_used_at', sa.DateTime(), nullable=True, comment='最后使用时间'),
    sa.Column('last_test_at', sa.DateTime(), nullable=True, comment='最后测试时间'),
    sa.Column('last_test_status', sa.String(length=20), nullable=True, comment='最后测试状态: success/failed'),
    sa.Column('last_test_message', sa.Text(), nullable=True, comment='最后测试消息'),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_providers_id'), 'ai_providers', ['id'], unique=False)
    op.create_index('ix_ai_providers_provider_type', 'ai_providers', ['provider_type'], unique=False)
    op.create_index('ix_ai_providers_enabled', 'ai_providers', ['enabled'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_ai_providers_enabled', table_name='ai_providers')
    op.drop_index('ix_ai_providers_provider_type', table_name='ai_providers')
    op.drop_index(op.f('ix_ai_providers_id'), table_name='ai_providers')
    op.drop_table('ai_providers')

    # Drop enum type
    aiprovidertype = postgresql.ENUM('openai', 'grok', 'google', name='aiprovidertype')
    aiprovidertype.drop(op.get_bind(), checkfirst=True)
