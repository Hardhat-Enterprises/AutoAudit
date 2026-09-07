"""Expand aws_connection table with full credential columns.

Revision ID: k1l2m3n4o567
Revises: 8a7b91ea95d9
Create Date: 2026-07-26
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "k1l2m3n4o567"
down_revision: Union[str, Sequence[str], None] = "8a7b91ea95d9"
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
    """Downgrade schema — remove only the columns added by this revision."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "aws_connection" not in set(inspector.get_table_names()):
        return

    existing_columns = {col["name"] for col in inspector.get_columns("aws_connection")}

    # Drop index first if it exists
    existing_indexes = {idx["name"] for idx in inspector.get_indexes("aws_connection")}
    if "ix_aws_connection_user_id" in existing_indexes:
        op.drop_index(op.f("ix_aws_connection_user_id"), table_name="aws_connection")

    # Drop only the columns added by this migration
    for col in ["updated_at", "created_at", "is_active", "region",
                "encrypted_secret_access_key", "access_key_id", "account_id", "name", "user_id"]:
        if col in existing_columns:
            op.drop_column("aws_connection", col)
