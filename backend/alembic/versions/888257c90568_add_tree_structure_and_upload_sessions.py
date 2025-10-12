"""add tree structure and upload sessions

Revision ID: 888257c90568
Revises: fa0203c7f3f7
Create Date: 2025-10-12 20:50:52.054871

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '888257c90568'
down_revision: Union[str, None] = 'fa0203c7f3f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 添加树形结构字段到 media 表
    op.add_column('media', sa.Column('parent_id', sa.Integer(), nullable=True, comment='父文件夹ID（NULL表示根目录）'))
    op.add_column('media', sa.Column('is_folder', sa.Boolean(), nullable=True, server_default='false', comment='是否为文件夹'))
    op.add_column('media', sa.Column('path', sa.String(length=1024), nullable=True, comment='完整路径（如：/root/folder1/folder2）'))

    # 创建索引
    op.create_index(op.f('ix_media_parent_id'), 'media', ['parent_id'], unique=False)
    op.create_index(op.f('ix_media_is_folder'), 'media', ['is_folder'], unique=False)

    # 创建外键约束（自引用）
    op.create_foreign_key('fk_media_parent_id', 'media', 'media', ['parent_id'], ['id'])

    # 创建上传会话表
    op.create_table('upload_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('upload_id', sa.String(length=64), nullable=False, comment='上传会话ID（UUID）'),
        sa.Column('filename', sa.String(length=255), nullable=False, comment='原始文件名'),
        sa.Column('file_size', sa.BigInteger(), nullable=False, comment='文件总大小（字节）'),
        sa.Column('mime_type', sa.String(length=100), nullable=True, comment='MIME类型'),
        sa.Column('chunk_size', sa.Integer(), nullable=True, server_default='5242880', comment='分块大小（默认5MB）'),
        sa.Column('total_chunks', sa.Integer(), nullable=False, comment='总分块数'),
        sa.Column('uploaded_chunks', postgresql.JSON(astext_type=sa.Text()), nullable=True, server_default='[]', comment='已上传的分块索引列表'),
        sa.Column('title', sa.String(length=255), nullable=False, comment='媒体标题'),
        sa.Column('description', sa.String(length=1000), nullable=True, comment='媒体描述'),
        sa.Column('parent_id', sa.Integer(), nullable=True, comment='父文件夹ID'),
        sa.Column('tags', sa.String(length=512), nullable=True, comment='标签'),
        sa.Column('temp_dir', sa.String(length=512), nullable=False, comment='临时分块存储目录'),
        sa.Column('is_completed', sa.Boolean(), nullable=True, server_default='false', comment='是否完成'),
        sa.Column('is_merged', sa.Boolean(), nullable=True, server_default='false', comment='是否已合并'),
        sa.Column('uploader_id', sa.Integer(), nullable=False, comment='上传者ID'),
        sa.Column('media_id', sa.Integer(), nullable=True, comment='完成后的媒体ID'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, comment='最后更新时间'),
        sa.Column('expires_at', sa.DateTime(), nullable=False, comment='过期时间'),
        sa.ForeignKeyConstraint(['media_id'], ['media.id'], ),
        sa.ForeignKeyConstraint(['parent_id'], ['media.id'], ),
        sa.ForeignKeyConstraint(['uploader_id'], ['admin_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_upload_sessions_id'), 'upload_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_upload_sessions_upload_id'), 'upload_sessions', ['upload_id'], unique=True)


def downgrade() -> None:
    # 删除上传会话表
    op.drop_index(op.f('ix_upload_sessions_upload_id'), table_name='upload_sessions')
    op.drop_index(op.f('ix_upload_sessions_id'), table_name='upload_sessions')
    op.drop_table('upload_sessions')

    # 删除 media 表的树形结构字段
    op.drop_constraint('fk_media_parent_id', 'media', type_='foreignkey')
    op.drop_index(op.f('ix_media_is_folder'), table_name='media')
    op.drop_index(op.f('ix_media_parent_id'), table_name='media')
    op.drop_column('media', 'path')
    op.drop_column('media', 'is_folder')
    op.drop_column('media', 'parent_id')
