"""add_system_monitoring_tables

Revision ID: 8340262353e7
Revises: f2af1dfc574d
Create Date: 2025-10-19 20:40:11.768338

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8340262353e7'
down_revision: Union[str, None] = 'f2af1dfc574d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create system_metrics table
    op.create_table(
        'system_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('cpu_usage_percent', sa.Float(), nullable=True),
        sa.Column('cpu_cores', sa.Integer(), nullable=True),
        sa.Column('memory_usage_percent', sa.Float(), nullable=True),
        sa.Column('memory_used_gb', sa.Float(), nullable=True),
        sa.Column('memory_total_gb', sa.Float(), nullable=True),
        sa.Column('memory_available_gb', sa.Float(), nullable=True),
        sa.Column('disk_usage_percent', sa.Float(), nullable=True),
        sa.Column('disk_used_gb', sa.Float(), nullable=True),
        sa.Column('disk_total_gb', sa.Float(), nullable=True),
        sa.Column('disk_free_gb', sa.Float(), nullable=True),
        sa.Column('network_bytes_sent_gb', sa.Float(), nullable=True),
        sa.Column('network_bytes_recv_gb', sa.Float(), nullable=True),
        sa.Column('network_errors', sa.Integer(), nullable=True),
        sa.Column('db_response_time_ms', sa.Float(), nullable=True),
        sa.Column('db_pool_size', sa.Integer(), nullable=True),
        sa.Column('db_pool_checked_out', sa.Integer(), nullable=True),
        sa.Column('db_pool_utilization', sa.Float(), nullable=True),
        sa.Column('redis_response_time_ms', sa.Float(), nullable=True),
        sa.Column('redis_used_memory_mb', sa.Float(), nullable=True),
        sa.Column('redis_memory_utilization', sa.Float(), nullable=True),
        sa.Column('redis_keys_count', sa.Integer(), nullable=True),
        sa.Column('storage_response_time_ms', sa.Float(), nullable=True),
        sa.Column('storage_used_gb', sa.Float(), nullable=True),
        sa.Column('storage_total_gb', sa.Float(), nullable=True),
        sa.Column('storage_utilization', sa.Float(), nullable=True),
        sa.Column('overall_status', sa.String(length=20), nullable=True),
        sa.Column('database_status', sa.String(length=20), nullable=True),
        sa.Column('redis_status', sa.String(length=20), nullable=True),
        sa.Column('storage_status', sa.String(length=20), nullable=True),
        sa.Column('process_count', sa.Integer(), nullable=True),
        sa.Column('celery_active_tasks', sa.Integer(), nullable=True),
        sa.Column('celery_workers_count', sa.Integer(), nullable=True),
        sa.Column('extra_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_system_metrics_timestamp', 'system_metrics', ['timestamp'])
    op.create_index('idx_system_metrics_status', 'system_metrics', ['overall_status'])
    op.create_index('idx_system_metrics_created_at', 'system_metrics', ['created_at'])
    op.create_index(op.f('ix_system_metrics_id'), 'system_metrics', ['id'])

    # Create system_alerts table
    op.create_table(
        'system_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('alert_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.String(length=1000), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=True),
        sa.Column('metric_value', sa.Float(), nullable=True),
        sa.Column('threshold_value', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('triggered_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notification_sent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('notification_channels', sa.String(length=200), nullable=True),
        sa.Column('acknowledged_by', sa.Integer(), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.String(length=1000), nullable=True),
        sa.Column('context', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_system_alerts_type_severity', 'system_alerts', ['alert_type', 'severity'])
    op.create_index('idx_system_alerts_status', 'system_alerts', ['status'])
    op.create_index('idx_system_alerts_triggered_at', 'system_alerts', ['triggered_at'])
    op.create_index(op.f('ix_system_alerts_id'), 'system_alerts', ['id'])

    # Create system_sla table
    op.create_table(
        'system_sla',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_type', sa.String(length=20), nullable=False),
        sa.Column('uptime_seconds', sa.Integer(), nullable=False),
        sa.Column('downtime_seconds', sa.Integer(), nullable=False),
        sa.Column('uptime_percentage', sa.Float(), nullable=False),
        sa.Column('total_requests', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('successful_requests', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failed_requests', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('avg_response_time_ms', sa.Float(), nullable=True),
        sa.Column('p50_response_time_ms', sa.Float(), nullable=True),
        sa.Column('p95_response_time_ms', sa.Float(), nullable=True),
        sa.Column('p99_response_time_ms', sa.Float(), nullable=True),
        sa.Column('max_response_time_ms', sa.Float(), nullable=True),
        sa.Column('total_alerts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('critical_alerts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('warning_alerts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('avg_cpu_usage', sa.Float(), nullable=True),
        sa.Column('avg_memory_usage', sa.Float(), nullable=True),
        sa.Column('avg_disk_usage', sa.Float(), nullable=True),
        sa.Column('extra_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_system_sla_period', 'system_sla', ['period_start', 'period_end'])
    op.create_index('idx_system_sla_type', 'system_sla', ['period_type'])
    op.create_index(op.f('ix_system_sla_id'), 'system_sla', ['id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_system_sla_id'), table_name='system_sla')
    op.drop_index('idx_system_sla_type', table_name='system_sla')
    op.drop_index('idx_system_sla_period', table_name='system_sla')
    op.drop_table('system_sla')

    op.drop_index(op.f('ix_system_alerts_id'), table_name='system_alerts')
    op.drop_index('idx_system_alerts_triggered_at', table_name='system_alerts')
    op.drop_index('idx_system_alerts_status', table_name='system_alerts')
    op.drop_index('idx_system_alerts_type_severity', table_name='system_alerts')
    op.drop_table('system_alerts')

    op.drop_index(op.f('ix_system_metrics_id'), table_name='system_metrics')
    op.drop_index('idx_system_metrics_created_at', table_name='system_metrics')
    op.drop_index('idx_system_metrics_status', table_name='system_metrics')
    op.drop_index('idx_system_metrics_timestamp', table_name='system_metrics')
    op.drop_table('system_metrics')
