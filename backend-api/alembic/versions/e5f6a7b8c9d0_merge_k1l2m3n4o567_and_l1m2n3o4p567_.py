"""merge k1l2m3n4o567 and l1m2n3o4p567 heads

Revision ID: e5f6a7b8c9d0
Revises: k1l2m3n4o567, l1m2n3o4p567
Create Date: 2026-09-08 00:00:00.000000

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, Sequence[str], None] = ('k1l2m3n4o567', 'l1m2n3o4p567')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema. No-op merge revision; reconciles the two heads."""


def downgrade() -> None:
    """Downgrade schema. No-op merge revision; reconciles the two heads."""
