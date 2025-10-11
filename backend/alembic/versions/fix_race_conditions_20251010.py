"""fix race conditions with database triggers

Revision ID: fix_race_conditions_20251010
Revises: 23014a639f71
Create Date: 2025-10-10 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fix_race_conditions_20251010'
down_revision: Union[str, None] = '23014a639f71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建触发器函数：自动更新视频评分统计
    op.execute("""
    CREATE OR REPLACE FUNCTION update_video_rating_stats()
    RETURNS TRIGGER AS $$
    DECLARE
        v_avg_rating FLOAT;
        v_count INTEGER;
    BEGIN
        -- 计算视频的平均分和评分数
        SELECT AVG(score), COUNT(*)
        INTO v_avg_rating, v_count
        FROM ratings
        WHERE video_id = COALESCE(NEW.video_id, OLD.video_id);
        
        -- 更新视频表
        UPDATE videos
        SET 
            average_rating = COALESCE(v_avg_rating, 0.0),
            rating_count = v_count
        WHERE id = COALESCE(NEW.video_id, OLD.video_id);
        
        RETURN COALESCE(NEW, OLD);
    END;
    $$ LANGUAGE plpgsql;
    """)
    
    # 创建触发器：INSERT时更新
    op.execute("""
    CREATE TRIGGER rating_insert_trigger
    AFTER INSERT ON ratings
    FOR EACH ROW
    EXECUTE FUNCTION update_video_rating_stats();
    """)
    
    # 创建触发器：UPDATE时更新
    op.execute("""
    CREATE TRIGGER rating_update_trigger
    AFTER UPDATE ON ratings
    FOR EACH ROW
    EXECUTE FUNCTION update_video_rating_stats();
    """)
    
    # 创建触发器：DELETE时更新
    op.execute("""
    CREATE TRIGGER rating_delete_trigger
    AFTER DELETE ON ratings
    FOR EACH ROW
    EXECUTE FUNCTION update_video_rating_stats();
    """)
    
    # 添加唯一约束：同一用户对同一视频只能有一个评分
    op.create_unique_constraint(
        'uq_ratings_user_video',
        'ratings',
        ['user_id', 'video_id']
    )
    
    # 添加唯一约束：同一用户对同一视频只能有一条观看历史
    op.create_unique_constraint(
        'uq_watch_history_user_video',
        'watch_history',
        ['user_id', 'video_id']
    )


def downgrade() -> None:
    # 删除触发器
    op.execute("DROP TRIGGER IF EXISTS rating_delete_trigger ON ratings;")
    op.execute("DROP TRIGGER IF EXISTS rating_update_trigger ON ratings;")
    op.execute("DROP TRIGGER IF EXISTS rating_insert_trigger ON ratings;")
    
    # 删除触发器函数
    op.execute("DROP FUNCTION IF EXISTS update_video_rating_stats();")
    
    # 删除唯一约束
    op.drop_constraint('uq_ratings_user_video', 'ratings', type_='unique')
    op.drop_constraint('uq_watch_history_user_video', 'watch_history', type_='unique')


