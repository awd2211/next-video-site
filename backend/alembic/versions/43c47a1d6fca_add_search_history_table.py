"""add search history table

Revision ID: 43c47a1d6fca
Revises: b6f5e78ad857
Create Date: 2025-10-13 23:15:28.851893

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '43c47a1d6fca'
down_revision: Union[str, None] = 'b6f5e78ad857'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create search_history table
    op.create_table(
        'search_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('query', sa.String(length=255), nullable=False),
        sa.Column('results_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('clicked_video_id', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['clicked_video_id'], ['videos.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for performance
    op.create_index(op.f('ix_search_history_id'), 'search_history', ['id'], unique=False)
    op.create_index(op.f('ix_search_history_user_id'), 'search_history', ['user_id'], unique=False)
    op.create_index(op.f('ix_search_history_query'), 'search_history', ['query'], unique=False)
    op.create_index(op.f('ix_search_history_created_at'), 'search_history', ['created_at'], unique=False)

    # Composite index for common query pattern: user's recent searches
    op.create_index('ix_search_history_user_created', 'search_history', ['user_id', 'created_at'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_search_history_user_created', table_name='search_history')
    op.drop_index(op.f('ix_search_history_created_at'), table_name='search_history')
    op.drop_index(op.f('ix_search_history_query'), table_name='search_history')
    op.drop_index(op.f('ix_search_history_user_id'), table_name='search_history')
    op.drop_index(op.f('ix_search_history_id'), table_name='search_history')

    # Drop table
    op.drop_table('search_history')
