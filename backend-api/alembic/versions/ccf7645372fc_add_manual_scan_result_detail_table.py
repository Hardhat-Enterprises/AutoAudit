"""add manual_scan_result_detail table

Revision ID: ccf7645372fc
Revises: j1k2l3m4n567
Create Date: 2026-04-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ccf7645372fc"
down_revision: Union[str, Sequence[str], None] = "j1k2l3m4n567"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "manual_scan_result_detail",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("scan_result_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["scan_result_id"], ["scan_result.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scan_result_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("manual_scan_result_detail")