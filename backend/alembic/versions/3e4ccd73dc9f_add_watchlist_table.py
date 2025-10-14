"""add_watchlist_table

Revision ID: 3e4ccd73dc9f
Revises: 43c47a1d6fca
Create Date: 2025-10-13 23:24:11.009298

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e4ccd73dc9f'
down_revision: Union[str, None] = '43c47a1d6fca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create watchlist table
    op.create_table(
        'watchlist',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('video_id', sa.Integer(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'video_id', name='uq_user_video_watchlist')
    )

    # Create indexes
    op.create_index('ix_watchlist_user_id', 'watchlist', ['user_id'])
    op.create_index('ix_watchlist_video_id', 'watchlist', ['video_id'])
    op.create_index('ix_watchlist_created_at', 'watchlist', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_watchlist_created_at', 'watchlist')
    op.drop_index('ix_watchlist_video_id', 'watchlist')
    op.drop_index('ix_watchlist_user_id', 'watchlist')

    # Drop table
    op.drop_table('watchlist')
