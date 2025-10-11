"""merge optimization branches

Revision ID: 1aefaf7eebdd
Revises: e18bbd33b0c7, add_fulltext_search_20251010
Create Date: 2025-10-11 00:37:31.997209

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1aefaf7eebdd'
down_revision: Union[str, None] = ('e18bbd33b0c7', 'add_fulltext_search_20251010')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
