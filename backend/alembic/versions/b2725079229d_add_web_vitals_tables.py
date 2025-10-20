"""add web vitals tables

Revision ID: b2725079229d
Revises: 8340262353e7
Create Date: 2025-10-20 00:54:50.926538

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2725079229d'
down_revision: Union[str, None] = '8340262353e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create web_vitals table
    op.create_table('web_vitals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('rating', sa.String(length=20), nullable=True),
        sa.Column('delta', sa.Float(), nullable=True),
        sa.Column('metric_id', sa.String(length=100), nullable=True),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_web_vitals_id', 'web_vitals', ['id'], unique=False)
    op.create_index('ix_web_vitals_name', 'web_vitals', ['name'], unique=False)
    op.create_index('ix_web_vitals_timestamp', 'web_vitals', ['timestamp'], unique=False)

    # Create page_performance table
    op.create_table('page_performance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('page_load_time', sa.Float(), nullable=True),
        sa.Column('dns_time', sa.Float(), nullable=True),
        sa.Column('tcp_time', sa.Float(), nullable=True),
        sa.Column('request_time', sa.Float(), nullable=True),
        sa.Column('response_time', sa.Float(), nullable=True),
        sa.Column('dom_processing', sa.Float(), nullable=True),
        sa.Column('dom_content_loaded', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_page_performance_created_at', 'page_performance', ['created_at'], unique=False)
    op.create_index('ix_page_performance_id', 'page_performance', ['id'], unique=False)
    op.create_index('ix_page_performance_url', 'page_performance', ['url'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_page_performance_url', table_name='page_performance')
    op.drop_index('ix_page_performance_id', table_name='page_performance')
    op.drop_index('ix_page_performance_created_at', table_name='page_performance')
    op.drop_table('page_performance')

    op.drop_index('ix_web_vitals_timestamp', table_name='web_vitals')
    op.drop_index('ix_web_vitals_name', table_name='web_vitals')
    op.drop_index('ix_web_vitals_id', table_name='web_vitals')
    op.drop_table('web_vitals')
