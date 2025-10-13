"""add video hash fields

Revision ID: b6f5e78ad857
Revises: 4e71195faee1
Create Date: 2025-10-13 11:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b6f5e78ad857'
down_revision: Union[str, None] = '4e71195faee1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add video hash fields for duplicate detection
    op.add_column('videos', sa.Column('file_hash_md5', sa.String(length=32), nullable=True, comment='完整文件MD5哈希'))
    op.add_column('videos', sa.Column('partial_hash', sa.String(length=32), nullable=True, comment='部分内容哈希(头+尾)'))
    op.add_column('videos', sa.Column('metadata_hash', sa.String(length=32), nullable=True, comment='元数据哈希(标题+时长+大小)'))
    op.create_index(op.f('ix_videos_file_hash_md5'), 'videos', ['file_hash_md5'], unique=False)
    op.create_index(op.f('ix_videos_metadata_hash'), 'videos', ['metadata_hash'], unique=False)
    op.create_index(op.f('ix_videos_partial_hash'), 'videos', ['partial_hash'], unique=False)


def downgrade() -> None:
    # Remove video hash fields
    op.drop_index(op.f('ix_videos_partial_hash'), table_name='videos')
    op.drop_index(op.f('ix_videos_metadata_hash'), table_name='videos')
    op.drop_index(op.f('ix_videos_file_hash_md5'), table_name='videos')
    op.drop_column('videos', 'metadata_hash')
    op.drop_column('videos', 'partial_hash')
    op.drop_column('videos', 'file_hash_md5')
