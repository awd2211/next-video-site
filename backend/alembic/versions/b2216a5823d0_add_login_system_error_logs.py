"""add_login_system_error_logs

Revision ID: b2216a5823d0
Revises: 0e8f9139d7ca
Create Date: 2025-10-13 10:07:13.333329

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2216a5823d0'
down_revision: Union[str, None] = '0e8f9139d7ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create login_logs table
    op.create_table('login_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_type', sa.String(length=20), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('username', sa.String(length=100), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('failure_reason', sa.String(length=200), nullable=True),
    sa.Column('ip_address', sa.String(length=50), nullable=False),
    sa.Column('user_agent', sa.String(length=500), nullable=True),
    sa.Column('location', sa.String(length=200), nullable=True),
    sa.Column('device_type', sa.String(length=50), nullable=True),
    sa.Column('browser', sa.String(length=100), nullable=True),
    sa.Column('os', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_login_logs_created_at'), 'login_logs', ['created_at'], unique=False)
    op.create_index(op.f('ix_login_logs_id'), 'login_logs', ['id'], unique=False)
    op.create_index(op.f('ix_login_logs_ip_address'), 'login_logs', ['ip_address'], unique=False)
    op.create_index(op.f('ix_login_logs_status'), 'login_logs', ['status'], unique=False)
    op.create_index(op.f('ix_login_logs_user_type'), 'login_logs', ['user_type'], unique=False)

    # Create system_logs table
    op.create_table('system_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('level', sa.String(length=20), nullable=False),
    sa.Column('category', sa.String(length=50), nullable=False),
    sa.Column('event', sa.String(length=100), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('details', sa.Text(), nullable=True),
    sa.Column('source', sa.String(length=200), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('user_type', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_logs_category'), 'system_logs', ['category'], unique=False)
    op.create_index(op.f('ix_system_logs_created_at'), 'system_logs', ['created_at'], unique=False)
    op.create_index(op.f('ix_system_logs_id'), 'system_logs', ['id'], unique=False)
    op.create_index(op.f('ix_system_logs_level'), 'system_logs', ['level'], unique=False)

    # Create error_logs table
    op.create_table('error_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('level', sa.String(length=20), nullable=False),
    sa.Column('error_type', sa.String(length=100), nullable=False),
    sa.Column('error_message', sa.Text(), nullable=False),
    sa.Column('traceback', sa.Text(), nullable=True),
    sa.Column('request_method', sa.String(length=10), nullable=True),
    sa.Column('request_url', sa.String(length=500), nullable=True),
    sa.Column('request_data', sa.Text(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('user_type', sa.String(length=20), nullable=True),
    sa.Column('ip_address', sa.String(length=50), nullable=True),
    sa.Column('user_agent', sa.String(length=500), nullable=True),
    sa.Column('status_code', sa.Integer(), nullable=True),
    sa.Column('resolved', sa.Boolean(), nullable=False),
    sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('resolved_by', sa.Integer(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['resolved_by'], ['admin_users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_error_logs_created_at'), 'error_logs', ['created_at'], unique=False)
    op.create_index(op.f('ix_error_logs_error_type'), 'error_logs', ['error_type'], unique=False)
    op.create_index(op.f('ix_error_logs_id'), 'error_logs', ['id'], unique=False)
    op.create_index(op.f('ix_error_logs_level'), 'error_logs', ['level'], unique=False)
    op.create_index(op.f('ix_error_logs_resolved'), 'error_logs', ['resolved'], unique=False)


def downgrade() -> None:
    # Drop error_logs table
    op.drop_index(op.f('ix_error_logs_resolved'), table_name='error_logs')
    op.drop_index(op.f('ix_error_logs_level'), table_name='error_logs')
    op.drop_index(op.f('ix_error_logs_id'), table_name='error_logs')
    op.drop_index(op.f('ix_error_logs_error_type'), table_name='error_logs')
    op.drop_index(op.f('ix_error_logs_created_at'), table_name='error_logs')
    op.drop_table('error_logs')

    # Drop system_logs table
    op.drop_index(op.f('ix_system_logs_level'), table_name='system_logs')
    op.drop_index(op.f('ix_system_logs_id'), table_name='system_logs')
    op.drop_index(op.f('ix_system_logs_created_at'), table_name='system_logs')
    op.drop_index(op.f('ix_system_logs_category'), table_name='system_logs')
    op.drop_table('system_logs')

    # Drop login_logs table
    op.drop_index(op.f('ix_login_logs_user_type'), table_name='login_logs')
    op.drop_index(op.f('ix_login_logs_status'), table_name='login_logs')
    op.drop_index(op.f('ix_login_logs_ip_address'), table_name='login_logs')
    op.drop_index(op.f('ix_login_logs_id'), table_name='login_logs')
    op.drop_index(op.f('ix_login_logs_created_at'), table_name='login_logs')
    op.drop_table('login_logs')
