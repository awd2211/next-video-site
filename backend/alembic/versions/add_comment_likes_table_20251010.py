"""add comment likes table for idempotency

Revision ID: add_comment_likes_table_20251010
Revises: fix_race_conditions_20251010
Create Date: 2025-10-10 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_comment_likes_table_20251010'
down_revision: Union[str, None] = 'fix_race_conditions_20251010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建用户评论点赞关联表
    op.create_table(
        'user_comment_likes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('comment_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['comment_id'], ['comments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 唯一约束：同一用户对同一评论只能点赞一次
    op.create_unique_constraint(
        'uq_user_comment_likes',
        'user_comment_likes',
        ['user_id', 'comment_id']
    )
    
    # 索引：查询用户是否点赞过某评论
    op.create_index(
        'idx_user_comment_likes_user',
        'user_comment_likes',
        ['user_id']
    )
    
    op.create_index(
        'idx_user_comment_likes_comment',
        'user_comment_likes',
        ['comment_id']
    )
    
    # 创建触发器：自动更新评论的like_count
    op.execute("""
    CREATE OR REPLACE FUNCTION update_comment_like_count()
    RETURNS TRIGGER AS $$
    BEGIN
        IF TG_OP = 'INSERT' THEN
            -- 点赞：增加计数
            UPDATE comments
            SET like_count = like_count + 1
            WHERE id = NEW.comment_id;
        ELSIF TG_OP = 'DELETE' THEN
            -- 取消点赞：减少计数
            UPDATE comments
            SET like_count = GREATEST(0, like_count - 1)
            WHERE id = OLD.comment_id;
        END IF;
        
        RETURN COALESCE(NEW, OLD);
    END;
    $$ LANGUAGE plpgsql;
    """)
    
    # 创建触发器
    op.execute("""
    CREATE TRIGGER comment_like_insert_trigger
    AFTER INSERT ON user_comment_likes
    FOR EACH ROW
    EXECUTE FUNCTION update_comment_like_count();
    """)
    
    op.execute("""
    CREATE TRIGGER comment_like_delete_trigger
    AFTER DELETE ON user_comment_likes
    FOR EACH ROW
    EXECUTE FUNCTION update_comment_like_count();
    """)


def downgrade() -> None:
    # 删除触发器
    op.execute("DROP TRIGGER IF EXISTS comment_like_delete_trigger ON user_comment_likes;")
    op.execute("DROP TRIGGER IF EXISTS comment_like_insert_trigger ON user_comment_likes;")
    
    # 删除触发器函数
    op.execute("DROP FUNCTION IF EXISTS update_comment_like_count();")
    
    # 删除索引
    op.drop_index('idx_user_comment_likes_comment', table_name='user_comment_likes')
    op.drop_index('idx_user_comment_likes_user', table_name='user_comment_likes')
    
    # 删除唯一约束
    op.drop_constraint('uq_user_comment_likes', 'user_comment_likes', type_='unique')
    
    # 删除表
    op.drop_table('user_comment_likes')


