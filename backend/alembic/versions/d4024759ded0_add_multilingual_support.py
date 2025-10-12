"""add_multilingual_support

Revision ID: d4024759ded0
Revises: 8a4017767dbd
Create Date: 2025-10-11 13:29:19.231557

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4024759ded0'
down_revision: Union[str, None] = '8a4017767dbd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 添加多语言字段到核心模型
    
    # 1. Category 多语言
    op.add_column('categories', sa.Column('name_en', sa.String(100), nullable=True, comment='英文名称'))
    op.add_column('categories', sa.Column('description_en', sa.Text, nullable=True, comment='英文描述'))
    
    # 2. Tag 多语言
    op.add_column('tags', sa.Column('name_en', sa.String(100), nullable=True, comment='英文名称'))
    
    # 3. Country 多语言
    op.add_column('countries', sa.Column('name_en', sa.String(100), nullable=True, comment='英文名称'))
    
    # 4. Announcement 多语言（检查表是否存在）
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'announcements' in inspector.get_table_names():
        op.add_column('announcements', sa.Column('title_en', sa.String(200), nullable=True, comment='英文标题'))
        op.add_column('announcements', sa.Column('content_en', sa.Text, nullable=True, comment='英文内容'))
    
    # 5. 填充默认数据（将中文复制到英文，方便后续翻译）
    op.execute("""
        UPDATE categories SET name_en = name, description_en = description WHERE name_en IS NULL;
        UPDATE tags SET name_en = name WHERE name_en IS NULL;
        UPDATE countries SET name_en = name WHERE name_en IS NULL;
    """)
    
    # 如果announcements表存在，也填充
    if 'announcements' in inspector.get_table_names():
        op.execute("""
            UPDATE announcements SET title_en = title, content_en = content WHERE title_en IS NULL;
        """)


def downgrade() -> None:
    # 删除多语言字段
    op.drop_column('categories', 'description_en')
    op.drop_column('categories', 'name_en')
    op.drop_column('tags', 'name_en')
    op.drop_column('countries', 'name_en')
    
    # 检查announcements表
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'announcements' in inspector.get_table_names():
        op.drop_column('announcements', 'content_en')
        op.drop_column('announcements', 'title_en')
