"""add_2fa_fields_to_admin_users

Revision ID: 8bdfb446659f
Revises: 087c0df2c53b
Create Date: 2025-10-14 01:27:47.135103

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8bdfb446659f'
down_revision: Union[str, None] = '087c0df2c53b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add 2FA fields to admin_users table
    op.add_column('admin_users', sa.Column('totp_enabled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('admin_users', sa.Column('totp_secret', sa.String(500), nullable=True))
    op.add_column('admin_users', sa.Column('backup_codes', sa.String(2000), nullable=True))
    op.add_column('admin_users', sa.Column('totp_verified_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Remove 2FA fields from admin_users table
    op.drop_column('admin_users', 'totp_verified_at')
    op.drop_column('admin_users', 'backup_codes')
    op.drop_column('admin_users', 'totp_secret')
    op.drop_column('admin_users', 'totp_enabled')
