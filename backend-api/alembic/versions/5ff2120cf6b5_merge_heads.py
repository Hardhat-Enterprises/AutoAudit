"""merge heads

Revision ID: 5ff2120cf6b5
Revises: ccf7645372fc, d87c3bb49953
Create Date: 2026-09-05 18:57:59.924840

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ff2120cf6b5'
down_revision: Union[str, Sequence[str], None] = ('ccf7645372fc', 'd87c3bb49953')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
