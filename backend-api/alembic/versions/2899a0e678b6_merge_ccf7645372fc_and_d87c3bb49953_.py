"""merge ccf7645372fc and d87c3bb49953 heads

Revision ID: 2899a0e678b6
Revises: ccf7645372fc, d87c3bb49953
Create Date: 2026-09-03 03:57:12.921437

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2899a0e678b6'
down_revision: Union[str, Sequence[str], None] = ('ccf7645372fc', 'd87c3bb49953')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
