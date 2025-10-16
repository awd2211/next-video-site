"""add_upload_statistics_table

Revision ID: c510827f253d
Revises: 5fb824f18e42
Create Date: 2025-10-16 10:33:47.663036

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c510827f253d'
down_revision: Union[str, None] = '5fb824f18e42'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建上传统计表
    op.create_table(
        'upload_statistics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('upload_id', sa.String(length=64), nullable=False, comment='上传会话ID'),
        sa.Column('filename', sa.String(length=255), nullable=False, comment='文件名'),
        sa.Column('file_size', sa.BigInteger(), nullable=False, comment='文件大小（字节）'),
        sa.Column('mime_type', sa.String(length=100), nullable=True, comment='MIME 类型'),
        sa.Column('upload_type', sa.String(length=50), nullable=True, comment='上传类型 (video/poster/backdrop)'),
        sa.Column('admin_id', sa.Integer(), nullable=False, comment='上传者ID'),
        sa.Column('total_chunks', sa.Integer(), nullable=True, comment='总分片数'),
        sa.Column('uploaded_chunks', sa.Integer(), nullable=True, comment='已上传分片数'),
        sa.Column('duration_seconds', sa.Float(), nullable=True, comment='上传耗时（秒）'),
        sa.Column('upload_speed', sa.Float(), nullable=True, comment='平均上传速度（字节/秒）'),
        sa.Column('object_name', sa.String(length=512), nullable=True, comment='MinIO 对象名称'),
        sa.Column('minio_upload_id', sa.String(length=255), nullable=True, comment='MinIO multipart upload ID'),
        sa.Column('is_success', sa.Boolean(), nullable=True, comment='是否成功'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),
        sa.Column('ip_address', sa.String(length=45), nullable=True, comment='上传者 IP 地址'),
        sa.Column('started_at', sa.DateTime(), nullable=False, comment='开始时间'),
        sa.Column('completed_at', sa.DateTime(), nullable=True, comment='完成时间'),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='记录创建时间'),
        sa.ForeignKeyConstraint(['admin_id'], ['admin_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_upload_statistics_id'), 'upload_statistics', ['id'], unique=False)
    op.create_index(op.f('ix_upload_statistics_upload_id'), 'upload_statistics', ['upload_id'], unique=False)


def downgrade() -> None:
    # 删除上传统计表
    op.drop_index(op.f('ix_upload_statistics_upload_id'), table_name='upload_statistics')
    op.drop_index(op.f('ix_upload_statistics_id'), table_name='upload_statistics')
    op.drop_table('upload_statistics')
