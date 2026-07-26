"""Expand aws_connection table with full credential columns.

Revision ID: k1l2m3n4o567
Revises: j2k3l4m5n678
Create Date: 2026-07-26
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "k1l2m3n4o567"
down_revision: Union[str, Sequence[str], None] = "j2k3l4m5n678"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "aws_connection" not in existing_tables:
        # Fresh install — create the full table
        op.create_table(
            "aws_connection",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("account_id", sa.String(length=20), nullable=False),
            sa.Column("access_key_id", sa.String(length=255), nullable=False),
            sa.Column("encrypted_secret_access_key", sa.Text(), nullable=False),
            sa.Column("region", sa.String(length=50), nullable=False, server_default="us-east-1"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_aws_connection_user_id"),
            "aws_connection",
            ["user_id"],
        )
        return

    # Table already exists (stub with only id column) — add the missing columns
    existing_columns = {col["name"] for col in inspector.get_columns("aws_connection")}

    if "user_id" not in existing_columns:
        op.add_column("aws_connection", sa.Column("user_id", sa.Integer(), nullable=False, server_default="0"))
        op.create_foreign_key(None, "aws_connection", "user", ["user_id"], ["id"])
        op.create_index(op.f("ix_aws_connection_user_id"), "aws_connection", ["user_id"])

    if "name" not in existing_columns:
        op.add_column("aws_connection", sa.Column("name", sa.String(length=255), nullable=False, server_default="default"))

    if "account_id" not in existing_columns:
        op.add_column("aws_connection", sa.Column("account_id", sa.String(length=20), nullable=False, server_default="000000000000"))

    if "access_key_id" not in existing_columns:
        op.add_column("aws_connection", sa.Column("access_key_id", sa.String(length=255), nullable=False, server_default=""))

    if "encrypted_secret_access_key" not in existing_columns:
        op.add_column("aws_connection", sa.Column("encrypted_secret_access_key", sa.Text(), nullable=False, server_default=""))

    if "region" not in existing_columns:
        op.add_column("aws_connection", sa.Column("region", sa.String(length=50), nullable=False, server_default="us-east-1"))

    if "is_active" not in existing_columns:
        op.add_column("aws_connection", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))

    if "created_at" not in existing_columns:
        op.add_column("aws_connection", sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False))

    if "updated_at" not in existing_columns:
        op.add_column("aws_connection", sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False))


def downgrade() -> None:
    """Downgrade schema — drop all added columns, revert to stub."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "aws_connection" not in set(inspector.get_table_names()):
        return

    op.drop_index(op.f("ix_aws_connection_user_id"), table_name="aws_connection")
    op.drop_table("aws_connection")
