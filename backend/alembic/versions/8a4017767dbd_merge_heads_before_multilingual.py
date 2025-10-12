"""merge_heads_before_multilingual

Revision ID: 8a4017767dbd
Revises: 1aefaf7eebdd, user_activity_idx_20251011
Create Date: 2025-10-11 13:29:07.488411

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a4017767dbd'
down_revision: Union[str, None] = ('1aefaf7eebdd', 'user_activity_idx_20251011')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
