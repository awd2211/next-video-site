"""add_dashboard_layouts_table

Revision ID: 4e71195faee1
Revises: a9358ea4bc18
Create Date: 2025-10-13 11:15:15.572751

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e71195faee1'
down_revision: Union[str, None] = 'a9358ea4bc18'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create dashboard_layouts table
    op.create_table(
        'dashboard_layouts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_user_id', sa.Integer(), nullable=False),
        sa.Column('layout_config', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['admin_user_id'], ['admin_users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('admin_user_id', name='uq_dashboard_layouts_admin_user_id')
    )

    # Create index
    op.create_index(op.f('ix_dashboard_layouts_admin_user_id'), 'dashboard_layouts', ['admin_user_id'], unique=True)


def downgrade() -> None:
    # Drop index
    op.drop_index(op.f('ix_dashboard_layouts_admin_user_id'), table_name='dashboard_layouts')

    # Drop table
    op.drop_table('dashboard_layouts')
