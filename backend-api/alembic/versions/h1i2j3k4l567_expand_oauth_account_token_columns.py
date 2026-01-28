"""Add oauth_account table (squashed).

This migration squashes the original two-step history:
- g7h8i9j0k123: create oauth_account table
- h1i2j3k4l567: expand token columns (access_token/refresh_token) to TEXT

We create the table in its final schema (token columns as TEXT) to avoid
needing a follow-up migration.

Revision ID: h1i2j3k4l567
Revises: f6c7d8e9f012
Create Date: 2025-12-27
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "h1i2j3k4l567"
down_revision: Union[str, Sequence[str], None] = "f6c7d8e9f012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
# Support databases that may already be stamped at the original create-table revision.
replaces: Union[str, Sequence[str], None] = ("g7h8i9j0k123",)


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    existing_tables = set(inspector.get_table_names())
    if "oauth_account" not in existing_tables:
        op.create_table(
            "oauth_account",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("oauth_name", sa.String(length=100), nullable=False),
            # Use TEXT for provider tokens (can exceed 1024 chars).
            sa.Column("access_token", sa.Text(), nullable=False),
            sa.Column("expires_at", sa.Integer(), nullable=True),
            sa.Column("refresh_token", sa.Text(), nullable=True),
            sa.Column("account_id", sa.String(length=320), nullable=False),
            sa.Column("account_email", sa.String(length=320), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "oauth_name",
                "account_id",
                name="uq_oauth_account_oauth_name_account_id",
            ),
        )

        op.create_index(
            op.f("ix_oauth_account_oauth_name"),
            "oauth_account",
            ["oauth_name"],
        )
        op.create_index(
            op.f("ix_oauth_account_account_id"),
            "oauth_account",
            ["account_id"],
        )
        op.create_index(
            op.f("ix_oauth_account_user_id"),
            "oauth_account",
            ["user_id"],
        )
        return

    # If the table already exists (e.g., database was created with the old migration),
    # ensure token columns are large enough.
    op.alter_column(
        "oauth_account",
        "access_token",
        existing_type=sa.String(length=1024),
        type_=sa.Text(),
        existing_nullable=False,
    )
    op.alter_column(
        "oauth_account",
        "refresh_token",
        existing_type=sa.String(length=1024),
        type_=sa.Text(),
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "oauth_account" not in set(inspector.get_table_names()):
        return

    # Drop indexes first (naming convention uses op.f()).
    op.drop_index(op.f("ix_oauth_account_user_id"), table_name="oauth_account")
    op.drop_index(op.f("ix_oauth_account_account_id"), table_name="oauth_account")
    op.drop_index(op.f("ix_oauth_account_oauth_name"), table_name="oauth_account")
    op.drop_table("oauth_account")













