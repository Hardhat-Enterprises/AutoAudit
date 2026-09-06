"""merge migration heads

Revision ID: fe2dba17ae7a
Revises: ccf7645372fc, d87c3bb49953
Create Date: 2026-08-21 00:00:00.000000

"""
from typing import Sequence, Union

revision: str = "fe2dba17ae7a"
down_revision: Union[str, Sequence[str], None] = ("ccf7645372fc", "d87c3bb49953")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
