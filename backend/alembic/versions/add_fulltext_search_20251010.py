"""add fulltext search support

Revision ID: add_fulltext_search_20251010
Revises: add_performance_indexes_20251010
Create Date: 2025-10-10 23:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import TSVECTOR


# revision identifiers, used by Alembic.
revision: str = "add_fulltext_search_20251010"
down_revision: Union[str, None] = "add_performance_indexes_20251010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 添加全文搜索向量列
    op.add_column("videos", sa.Column("search_vector", TSVECTOR, nullable=True))

    # 创建GIN索引用于全文搜索
    op.execute(
        """
    CREATE INDEX idx_videos_search_vector 
    ON videos 
    USING GIN (search_vector);
    """
    )

    # 创建触发器函数：自动更新搜索向量
    op.execute(
        """
    CREATE OR REPLACE FUNCTION update_video_search_vector()
    RETURNS TRIGGER AS $$
    BEGIN
        -- 组合标题、原始标题和描述创建搜索向量
        -- 使用中文分词配置（如果有）或默认配置
        NEW.search_vector := 
            setweight(to_tsvector('simple', COALESCE(NEW.title, '')), 'A') ||
            setweight(to_tsvector('simple', COALESCE(NEW.original_title, '')), 'B') ||
            setweight(to_tsvector('simple', COALESCE(NEW.description, '')), 'C');
        
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """
    )

    # 创建触发器
    op.execute(
        """
    CREATE TRIGGER video_search_vector_update
    BEFORE INSERT OR UPDATE ON videos
    FOR EACH ROW
    EXECUTE FUNCTION update_video_search_vector();
    """
    )

    # 为现有数据生成搜索向量
    op.execute(
        """
    UPDATE videos
    SET search_vector = 
        setweight(to_tsvector('simple', COALESCE(title, '')), 'A') ||
        setweight(to_tsvector('simple', COALESCE(original_title, '')), 'B') ||
        setweight(to_tsvector('simple', COALESCE(description, '')), 'C');
    """
    )


def downgrade() -> None:
    # 删除触发器
    op.execute("DROP TRIGGER IF EXISTS video_search_vector_update ON videos;")

    # 删除触发器函数
    op.execute("DROP FUNCTION IF EXISTS update_video_search_vector();")

    # 删除索引
    op.drop_index("idx_videos_search_vector", table_name="videos")

    # 删除列
    op.drop_column("videos", "search_vector")
