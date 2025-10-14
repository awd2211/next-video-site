"""add_oauth_support

Revision ID: 087c0df2c53b
Revises: becf37a05a4d
Create Date: 2025-10-14 01:16:30.062077

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '087c0df2c53b'
down_revision: Union[str, None] = 'becf37a05a4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create oauth_configs table
    op.create_table(
        'oauth_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('client_id', sa.String(length=500), nullable=False),
        sa.Column('client_secret', sa.Text(), nullable=False),
        sa.Column('redirect_uri', sa.String(length=500), nullable=True),
        sa.Column('scopes', sa.JSON(), nullable=True),
        sa.Column('authorization_url', sa.String(length=500), nullable=True),
        sa.Column('token_url', sa.String(length=500), nullable=True),
        sa.Column('userinfo_url', sa.String(length=500), nullable=True),
        sa.Column('extra_config', sa.JSON(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_test_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_test_status', sa.String(length=20), nullable=True),
        sa.Column('last_test_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_oauth_configs_id'), 'oauth_configs', ['id'], unique=False)
    op.create_index(op.f('ix_oauth_configs_provider'), 'oauth_configs', ['provider'], unique=True)

    # Add OAuth fields to users table
    op.add_column('users', sa.Column('oauth_provider', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('oauth_id', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('oauth_email', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('oauth_avatar', sa.String(length=500), nullable=True))
    op.create_index(op.f('ix_users_oauth_id'), 'users', ['oauth_id'], unique=False)

    # Make hashed_password nullable for OAuth users
    op.alter_column('users', 'hashed_password',
                    existing_type=sa.String(length=255),
                    nullable=True)


def downgrade() -> None:
    # Remove OAuth fields from users table
    op.drop_index(op.f('ix_users_oauth_id'), table_name='users')
    op.drop_column('users', 'oauth_avatar')
    op.drop_column('users', 'oauth_email')
    op.drop_column('users', 'oauth_id')
    op.drop_column('users', 'oauth_provider')

    # Make hashed_password non-nullable again
    op.alter_column('users', 'hashed_password',
                    existing_type=sa.String(length=255),
                    nullable=False)

    # Drop oauth_configs table
    op.drop_index(op.f('ix_oauth_configs_provider'), table_name='oauth_configs')
    op.drop_index(op.f('ix_oauth_configs_id'), table_name='oauth_configs')
    op.drop_table('oauth_configs')
