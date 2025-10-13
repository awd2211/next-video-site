"""add_admin_notifications_table

Revision ID: f0deea5e91de
Revises: b2216a5823d0
Create Date: 2025-10-13 11:06:56.242925

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f0deea5e91de'
down_revision: Union[str, None] = 'b2216a5823d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create admin_notifications table
    op.create_table(
        'admin_notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_user_id', sa.Integer(), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False, server_default='info'),
        sa.Column('related_type', sa.String(length=50), nullable=True),
        sa.Column('related_id', sa.Integer(), nullable=True),
        sa.Column('link', sa.String(length=500), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['admin_user_id'], ['admin_users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index(op.f('ix_admin_notifications_admin_user_id'), 'admin_notifications', ['admin_user_id'], unique=False)
    op.create_index(op.f('ix_admin_notifications_created_at'), 'admin_notifications', ['created_at'], unique=False)
    op.create_index(op.f('ix_admin_notifications_is_read'), 'admin_notifications', ['is_read'], unique=False)
    op.create_index(op.f('ix_admin_notifications_type'), 'admin_notifications', ['type'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_admin_notifications_type'), table_name='admin_notifications')
    op.drop_index(op.f('ix_admin_notifications_is_read'), table_name='admin_notifications')
    op.drop_index(op.f('ix_admin_notifications_created_at'), table_name='admin_notifications')
    op.drop_index(op.f('ix_admin_notifications_admin_user_id'), table_name='admin_notifications')

    # Drop table
    op.drop_table('admin_notifications')
