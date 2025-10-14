"""add AI enhanced features: logs, quotas, templates, performance metrics

Revision ID: ai_enhanced_001
Revises: 98c4f79e2b55
Create Date: 2025-10-14 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ai_enhanced_001'
down_revision: Union[str, None] = '98c4f79e2b55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # AI Request Logs
    op.create_table(
        'ai_request_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider_id', sa.Integer(), nullable=True),
        sa.Column('provider_type', sa.String(length=50), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('request_type', sa.String(length=50), nullable=True),
        sa.Column('prompt', sa.Text(), nullable=True),
        sa.Column('response', sa.Text(), nullable=True),
        sa.Column('prompt_tokens', sa.Integer(), nullable=True),
        sa.Column('completion_tokens', sa.Integer(), nullable=True),
        sa.Column('total_tokens', sa.Integer(), nullable=True),
        sa.Column('response_time', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('estimated_cost', sa.Float(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('admin_user_id', sa.Integer(), nullable=True),
        sa.Column('request_metadata', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['admin_user_id'], ['admin_users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['provider_id'], ['ai_providers.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_request_logs_created_at'), 'ai_request_logs', ['created_at'], unique=False)
    op.create_index(op.f('ix_ai_request_logs_provider_type'), 'ai_request_logs', ['provider_type'], unique=False)
    op.create_index(op.f('ix_ai_request_logs_total_tokens'), 'ai_request_logs', ['total_tokens'], unique=False)

    # AI Quotas
    op.create_table(
        'ai_quotas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('quota_type', sa.String(length=50), nullable=True),
        sa.Column('target_id', sa.Integer(), nullable=True),
        sa.Column('daily_request_limit', sa.Integer(), nullable=True),
        sa.Column('monthly_request_limit', sa.Integer(), nullable=True),
        sa.Column('daily_token_limit', sa.Integer(), nullable=True),
        sa.Column('monthly_token_limit', sa.Integer(), nullable=True),
        sa.Column('daily_cost_limit', sa.Float(), nullable=True),
        sa.Column('monthly_cost_limit', sa.Float(), nullable=True),
        sa.Column('daily_requests_used', sa.Integer(), nullable=True),
        sa.Column('daily_tokens_used', sa.Integer(), nullable=True),
        sa.Column('daily_cost_used', sa.Float(), nullable=True),
        sa.Column('monthly_requests_used', sa.Integer(), nullable=True),
        sa.Column('monthly_tokens_used', sa.Integer(), nullable=True),
        sa.Column('monthly_cost_used', sa.Float(), nullable=True),
        sa.Column('rate_limit_per_minute', sa.Integer(), nullable=True),
        sa.Column('rate_limit_per_hour', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_daily_reset', sa.DateTime(), nullable=True),
        sa.Column('last_monthly_reset', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # AI Templates
    op.create_table(
        'ai_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('prompt_template', sa.Text(), nullable=False),
        sa.Column('variables', sa.JSON(), nullable=True),
        sa.Column('recommended_provider', sa.String(length=50), nullable=True),
        sa.Column('recommended_model', sa.String(length=100), nullable=True),
        sa.Column('recommended_temperature', sa.Float(), nullable=True),
        sa.Column('recommended_max_tokens', sa.Integer(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=True),
        sa.Column('tags', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['admin_users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_templates_category'), 'ai_templates', ['category'], unique=False)

    # AI Performance Metrics
    op.create_table(
        'ai_performance_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider_type', sa.String(length=50), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('hour_bucket', sa.DateTime(), nullable=False),
        sa.Column('total_requests', sa.Integer(), nullable=True),
        sa.Column('successful_requests', sa.Integer(), nullable=True),
        sa.Column('failed_requests', sa.Integer(), nullable=True),
        sa.Column('avg_response_time', sa.Float(), nullable=True),
        sa.Column('min_response_time', sa.Float(), nullable=True),
        sa.Column('max_response_time', sa.Float(), nullable=True),
        sa.Column('p50_response_time', sa.Float(), nullable=True),
        sa.Column('p95_response_time', sa.Float(), nullable=True),
        sa.Column('p99_response_time', sa.Float(), nullable=True),
        sa.Column('total_tokens', sa.Integer(), nullable=True),
        sa.Column('avg_tokens_per_request', sa.Float(), nullable=True),
        sa.Column('total_cost', sa.Float(), nullable=True),
        sa.Column('avg_cost_per_request', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_performance_metrics_hour_bucket'), 'ai_performance_metrics', ['hour_bucket'], unique=False)
    op.create_index(op.f('ix_ai_performance_metrics_provider_type'), 'ai_performance_metrics', ['provider_type'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_ai_performance_metrics_provider_type'), table_name='ai_performance_metrics')
    op.drop_index(op.f('ix_ai_performance_metrics_hour_bucket'), table_name='ai_performance_metrics')
    op.drop_table('ai_performance_metrics')
    op.drop_index(op.f('ix_ai_templates_category'), table_name='ai_templates')
    op.drop_table('ai_templates')
    op.drop_table('ai_quotas')
    op.drop_index(op.f('ix_ai_request_logs_total_tokens'), table_name='ai_request_logs')
    op.drop_index(op.f('ix_ai_request_logs_provider_type'), table_name='ai_request_logs')
    op.drop_index(op.f('ix_ai_request_logs_created_at'), table_name='ai_request_logs')
    op.drop_table('ai_request_logs')
