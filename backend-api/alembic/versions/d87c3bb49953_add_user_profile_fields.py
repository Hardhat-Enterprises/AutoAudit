"""add user profile fields

Revision ID: d87c3bb49953
Revises: j1k2l3m4n567
Create Date: 2026-05-08 06:36:06.259229

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d87c3bb49953"
down_revision: Union[str, Sequence[str], None] = "j1k2l3m4n567"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user",
        sa.Column("first_name", sa.String(length=100), nullable=True),
    )

    op.add_column(
        "user",
        sa.Column("last_name", sa.String(length=100), nullable=True),
    )

    op.add_column(
        "user",
        sa.Column("organization_name", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("user", "organization_name")
    op.drop_column("user", "last_name")
    op.drop_column("user", "first_name")