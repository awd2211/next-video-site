"""Create payment subscription system tables

Revision ID: fedf46cf2fe8
Revises: 67b49f079f01
Create Date: 2025-10-19 08:21:00.199145

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fedf46cf2fe8'
down_revision: Union[str, None] = '67b49f079f01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
