"""Expand azure_connection table with full credential columns.

Revision ID: l1m2n3o4p567
Revises: k1l2m3n4o567
Create Date: 2026-08-08
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "l1m2n3o4p567"
down_revision: Union[str, Sequence[str], None] = "k1l2m3n4o567"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "azure_connection" not in existing_tables:
        # Fresh install — create the full table
        op.create_table(
            "azure_connection",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("tenant_id", sa.String(length=255), nullable=False),
            sa.Column("client_id", sa.String(length=255), nullable=False),
            sa.Column("encrypted_client_secret", sa.Text(), nullable=False),
            sa.Column("subscription_id", sa.String(length=255), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_azure_connection_user_id"),
            "azure_connection",
            ["user_id"],
        )
        return

    # Table already exists (stub with only id column) — add the missing columns
    existing_columns = {col["name"] for col in inspector.get_columns("azure_connection")}

    if "user_id" not in existing_columns:
        op.add_column("azure_connection", sa.Column("user_id", sa.Integer(), nullable=False, server_default="0"))
        op.create_foreign_key(None, "azure_connection", "user", ["user_id"], ["id"])
        op.create_index(op.f("ix_azure_connection_user_id"), "azure_connection", ["user_id"])

    if "name" not in existing_columns:
        op.add_column("azure_connection", sa.Column("name", sa.String(length=255), nullable=False, server_default="default"))

    if "tenant_id" not in existing_columns:
        op.add_column("azure_connection", sa.Column("tenant_id", sa.String(length=255), nullable=False, server_default=""))

    if "client_id" not in existing_columns:
        op.add_column("azure_connection", sa.Column("client_id", sa.String(length=255), nullable=False, server_default=""))

    if "encrypted_client_secret" not in existing_columns:
        op.add_column("azure_connection", sa.Column("encrypted_client_secret", sa.Text(), nullable=False, server_default=""))

    if "subscription_id" not in existing_columns:
        op.add_column("azure_connection", sa.Column("subscription_id", sa.String(length=255), nullable=False, server_default=""))

    if "is_active" not in existing_columns:
        op.add_column("azure_connection", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))

    if "created_at" not in existing_columns:
        op.add_column("azure_connection", sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False))

    if "updated_at" not in existing_columns:
        op.add_column("azure_connection", sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False))


def downgrade() -> None:
    """Downgrade schema — drop table entirely."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "azure_connection" not in set(inspector.get_table_names()):
        return

    op.drop_index(op.f("ix_azure_connection_user_id"), table_name="azure_connection")
    op.drop_table("azure_connection")
