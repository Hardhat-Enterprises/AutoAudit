"""Add m365_connection table and update scan table

Revision ID: c3d4e5f6g789
Revises: b1c2d3e4f567
Create Date: 2024-12-09

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6g789"
down_revision: Union[str, Sequence[str], None] = "b1c2d3e4f567"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add m365_connection table, update scan table, drop tenant table."""

    # Create m365_connection table
    op.create_table(
        "m365_connection",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("tenant_id", sa.String(length=255), nullable=False),
        sa.Column("client_id", sa.String(length=255), nullable=False),
        sa.Column("encrypted_client_secret", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_m365_connection_user_id"),
        "m365_connection",
        ["user_id"],
        unique=False,
    )

    # Update scan table: add new columns
    op.add_column(
        "scan",
        sa.Column("m365_connection_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "scan",
        sa.Column("framework", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "scan",
        sa.Column("benchmark", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "scan",
        sa.Column("version", sa.String(length=20), nullable=True),
    )
    op.add_column(
        "scan",
        sa.Column(
            "control_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
    )

    # Add control_id to issue table
    op.add_column(
        "issue",
        sa.Column("control_id", sa.String(length=50), nullable=True),
    )

    # Create foreign key for m365_connection_id
    op.create_foreign_key(
        "fk_scan_m365_connection_id",
        "scan",
        "m365_connection",
        ["m365_connection_id"],
        ["id"],
    )
    op.create_index(
        op.f("ix_scan_m365_connection_id"),
        "scan",
        ["m365_connection_id"],
        unique=False,
    )

    # Drop tenant_id FK and column from scan
    op.drop_index(op.f("ix_scan_tenant_id"), table_name="scan")
    op.drop_constraint("scan_tenant_id_fkey", "scan", type_="foreignkey")
    op.drop_column("scan", "tenant_id")

    # Drop tenant table
    op.drop_table("tenant")

    # Make framework/benchmark/version NOT NULL for new scans
    # (existing rows need to be handled - setting defaults first)
    op.execute("UPDATE scan SET framework = 'unknown' WHERE framework IS NULL")
    op.execute("UPDATE scan SET benchmark = 'unknown' WHERE benchmark IS NULL")
    op.execute("UPDATE scan SET version = 'unknown' WHERE version IS NULL")

    op.alter_column("scan", "framework", nullable=False)
    op.alter_column("scan", "benchmark", nullable=False)
    op.alter_column("scan", "version", nullable=False)


def downgrade() -> None:
    """Reverse the migration."""

    # Make framework/benchmark/version nullable again
    op.alter_column("scan", "version", nullable=True)
    op.alter_column("scan", "benchmark", nullable=True)
    op.alter_column("scan", "framework", nullable=True)

    # Recreate tenant table
    op.create_table(
        "tenant",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("external_tenant_id", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Add tenant_id back to scan
    op.add_column(
        "scan",
        sa.Column("tenant_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "scan_tenant_id_fkey", "scan", "tenant", ["tenant_id"], ["id"]
    )
    op.create_index(op.f("ix_scan_tenant_id"), "scan", ["tenant_id"], unique=False)

    # Drop m365_connection references from scan
    op.drop_index(op.f("ix_scan_m365_connection_id"), table_name="scan")
    op.drop_constraint("fk_scan_m365_connection_id", "scan", type_="foreignkey")

    # Drop new columns from issue
    op.drop_column("issue", "control_id")

    # Drop new columns from scan
    op.drop_column("scan", "control_ids")
    op.drop_column("scan", "version")
    op.drop_column("scan", "benchmark")
    op.drop_column("scan", "framework")
    op.drop_column("scan", "m365_connection_id")

    # Drop m365_connection table
    op.drop_index(op.f("ix_m365_connection_user_id"), table_name="m365_connection")
    op.drop_table("m365_connection")
