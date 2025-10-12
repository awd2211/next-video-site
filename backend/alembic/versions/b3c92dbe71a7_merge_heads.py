"""merge_heads

Revision ID: b3c92dbe71a7
Revises: 35059af975c3, d4024759ded0
Create Date: 2025-10-11 13:46:08.871597

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3c92dbe71a7'
down_revision: Union[str, None] = ('35059af975c3', 'd4024759ded0')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
