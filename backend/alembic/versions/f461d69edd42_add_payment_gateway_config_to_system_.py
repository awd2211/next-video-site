"""add_payment_gateway_config_to_system_settings

Revision ID: f461d69edd42
Revises: fedf46cf2fe8
Create Date: 2025-10-19 09:16:55.552030

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f461d69edd42'
down_revision: Union[str, None] = 'fedf46cf2fe8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 添加支付网关配置字段到 system_settings 表
    op.add_column('system_settings', sa.Column('payment_gateway_config', sa.JSON(), nullable=True))


def downgrade() -> None:
    # 移除支付网关配置字段
    op.drop_column('system_settings', 'payment_gateway_config')
