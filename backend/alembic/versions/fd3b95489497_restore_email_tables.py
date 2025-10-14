"""restore_email_tables

Revision ID: fd3b95489497
Revises: da7a0e6c92ef
Create Date: 2025-10-14 04:44:11.483028

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fd3b95489497'
down_revision: Union[str, None] = 'da7a0e6c92ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Restore email_configurations table (accidentally dropped in migration 23014a639f71)
    op.create_table(
        'email_configurations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('smtp_host', sa.String(length=255), nullable=True),
        sa.Column('smtp_port', sa.Integer(), nullable=True),
        sa.Column('smtp_username', sa.String(length=255), nullable=True),
        sa.Column('smtp_password', sa.String(length=255), nullable=True),
        sa.Column('smtp_use_tls', sa.Boolean(), nullable=True),
        sa.Column('smtp_use_ssl', sa.Boolean(), nullable=True),
        sa.Column('mailgun_api_key', sa.String(length=255), nullable=True),
        sa.Column('mailgun_domain', sa.String(length=255), nullable=True),
        sa.Column('mailgun_base_url', sa.String(length=255), nullable=True),
        sa.Column('from_email', sa.String(length=255), nullable=False),
        sa.Column('from_name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Restore email_templates table (accidentally dropped in migration 23014a639f71)
    op.create_table(
        'email_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('html_content', sa.Text(), nullable=False),
        sa.Column('text_content', sa.Text(), nullable=True),
        sa.Column('variables', sa.JSON(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )


def downgrade() -> None:
    op.drop_table('email_templates')
    op.drop_table('email_configurations')
