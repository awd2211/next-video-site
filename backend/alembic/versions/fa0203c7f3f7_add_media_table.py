"""add_media_table

Revision ID: fa0203c7f3f7
Revises: cef137ed97dc
Create Date: 2025-10-12 20:33:03.108768

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa0203c7f3f7'
down_revision: Union[str, None] = 'cef137ed97dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create media table
    op.create_table(
        'media',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False, comment='标题'),
        sa.Column('description', sa.Text(), nullable=True, comment='描述'),
        sa.Column('filename', sa.String(length=255), nullable=False, comment='原始文件名'),
        sa.Column('file_path', sa.String(length=512), nullable=False, comment='文件存储路径'),
        sa.Column('file_size', sa.BigInteger(), nullable=False, comment='文件大小(字节)'),
        sa.Column('mime_type', sa.String(length=100), nullable=True, comment='MIME类型'),
        sa.Column('media_type', sa.Enum('IMAGE', 'VIDEO', name='mediatype'), nullable=False, comment='媒体类型'),
        sa.Column('status', sa.Enum('UPLOADING', 'PROCESSING', 'READY', 'FAILED', name='mediastatus'), nullable=False, comment='状态'),
        sa.Column('width', sa.Integer(), nullable=True, comment='宽度(像素)'),
        sa.Column('height', sa.Integer(), nullable=True, comment='高度(像素)'),
        sa.Column('duration', sa.Integer(), nullable=True, comment='时长(秒)'),
        sa.Column('thumbnail_path', sa.String(length=512), nullable=True, comment='缩略图路径'),
        sa.Column('url', sa.String(length=512), nullable=True, comment='访问URL'),
        sa.Column('thumbnail_url', sa.String(length=512), nullable=True, comment='缩略图URL'),
        sa.Column('folder', sa.String(length=255), nullable=True, comment='文件夹/分类'),
        sa.Column('tags', sa.String(length=512), nullable=True, comment='标签(逗号分隔)'),
        sa.Column('view_count', sa.Integer(), nullable=True, server_default='0', comment='查看次数'),
        sa.Column('download_count', sa.Integer(), nullable=True, server_default='0', comment='下载次数'),
        sa.Column('uploader_id', sa.Integer(), nullable=False, comment='上传者ID'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, comment='更新时间'),
        sa.Column('is_deleted', sa.Boolean(), nullable=True, server_default='false', comment='是否已删除'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True, comment='删除时间'),
        sa.ForeignKeyConstraint(['uploader_id'], ['admin_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index(op.f('ix_media_id'), 'media', ['id'], unique=False)
    op.create_index(op.f('ix_media_title'), 'media', ['title'], unique=False)
    op.create_index(op.f('ix_media_media_type'), 'media', ['media_type'], unique=False)
    op.create_index(op.f('ix_media_status'), 'media', ['status'], unique=False)
    op.create_index(op.f('ix_media_folder'), 'media', ['folder'], unique=False)
    op.create_index(op.f('ix_media_is_deleted'), 'media', ['is_deleted'], unique=False)
    op.create_index(op.f('ix_media_file_path'), 'media', ['file_path'], unique=True)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_media_file_path'), table_name='media')
    op.drop_index(op.f('ix_media_is_deleted'), table_name='media')
    op.drop_index(op.f('ix_media_folder'), table_name='media')
    op.drop_index(op.f('ix_media_status'), table_name='media')
    op.drop_index(op.f('ix_media_media_type'), table_name='media')
    op.drop_index(op.f('ix_media_title'), table_name='media')
    op.drop_index(op.f('ix_media_id'), table_name='media')

    # Drop table
    op.drop_table('media')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS mediatype')
    op.execute('DROP TYPE IF EXISTS mediastatus')
