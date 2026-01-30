"""Add user_settings table.

Revision ID: j2k3l4m5n678
Revises: h1i2j3k4l567
Create Date: 2026-01-18
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "j2k3l4m5n678"
down_revision: Union[str, Sequence[str], None] = "h1i2j3k4l567"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "confirm_delete_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            onupdate=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_user_settings_user_id"),
    )

    op.create_index(
        op.f("ix_user_settings_user_id"),
        "user_settings",
        ["user_id"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_user_settings_user_id"), table_name="user_settings")
    op.drop_table("user_settings")

