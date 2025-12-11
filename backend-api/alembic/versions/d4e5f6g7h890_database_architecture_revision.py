"""Database architecture revision

- Create platform lookup table with seed data
- Create stub connection tables (azure, gcp, aws)
- Create scan_result table (replaces issue)
- Update scan table: add user_id FK, connection FKs, drop control_ids, add skipped_count, rename not_tested_count
- Drop issue and rule tables

Revision ID: d4e5f6g7h890
Revises: c3d4e5f6g789
Create Date: 2024-12-10

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "d4e5f6g7h890"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6g789"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply database architecture revision."""

    # 1. Create platform lookup table
    op.create_table(
        "platform",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="false"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # Seed platform data - only M365 is active
    op.execute("""
        INSERT INTO platform (name, display_name, is_active) VALUES
        ('m365', 'Microsoft 365', true),
        ('azure', 'Microsoft Azure', false),
        ('gcp', 'Google Cloud Platform', false),
        ('aws', 'Amazon Web Services', false)
    """)

    # 2. Create stub connection tables (id only - columns added when implemented)
    op.create_table(
        "azure_connection",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "gcp_connection",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "aws_connection",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # 3. Create scan_result table (replaces issue)
    op.create_table(
        "scan_result",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("scan_id", sa.Integer(), nullable=False),
        sa.Column("control_id", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("evidence", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["scan_id"], ["scan.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scan_id", "control_id", name="uq_scan_result_scan_control"),
    )
    op.create_index(
        op.f("ix_scan_result_scan_id"), "scan_result", ["scan_id"], unique=False
    )

    # 4. Update scan table
    # Add user_id FK (NOT NULL - starting fresh, but we need to handle existing rows)
    op.add_column("scan", sa.Column("user_id", sa.Integer(), nullable=True))

    # For any existing scans, assign them to user 1 (admin) if exists
    # In practice, we're starting fresh so this shouldn't matter
    op.execute("""
        UPDATE scan SET user_id = (SELECT id FROM "user" LIMIT 1)
        WHERE user_id IS NULL
    """)

    # Now make user_id NOT NULL
    op.alter_column("scan", "user_id", nullable=False)

    op.create_foreign_key(
        "fk_scan_user_id", "scan", "user", ["user_id"], ["id"]
    )
    op.create_index(op.f("ix_scan_user_id"), "scan", ["user_id"], unique=False)

    # Add connection FKs with actual foreign key constraints
    op.add_column(
        "scan", sa.Column("azure_connection_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        "fk_scan_azure_connection_id",
        "scan",
        "azure_connection",
        ["azure_connection_id"],
        ["id"],
    )

    op.add_column(
        "scan", sa.Column("gcp_connection_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        "fk_scan_gcp_connection_id",
        "scan",
        "gcp_connection",
        ["gcp_connection_id"],
        ["id"],
    )

    op.add_column(
        "scan", sa.Column("aws_connection_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        "fk_scan_aws_connection_id",
        "scan",
        "aws_connection",
        ["aws_connection_id"],
        ["id"],
    )

    # Remove control_ids - ScanResult records track selection
    op.drop_column("scan", "control_ids")

    # Rename not_tested_count to error_count
    op.alter_column("scan", "not_tested_count", new_column_name="error_count")

    # Add skipped_count
    op.add_column(
        "scan",
        sa.Column("skipped_count", sa.Integer(), nullable=False, server_default="0"),
    )

    # 5. Drop issue table (replaced by scan_result)
    op.drop_index(op.f("ix_issue_scan_id"), table_name="issue")
    op.drop_table("issue")

    # 6. Drop rule table (unused)
    op.drop_table("rule")


def downgrade() -> None:
    """Reverse the database architecture revision."""

    # 1. Recreate rule table
    op.create_table(
        "rule",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("framework", sa.String(length=100), nullable=False),
        sa.Column("control_key", sa.String(length=100), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # 2. Recreate issue table
    op.create_table(
        "issue",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("scan_id", sa.Integer(), nullable=False),
        sa.Column("rule_id", sa.Integer(), nullable=True),
        sa.Column("control_id", sa.String(length=50), nullable=True),
        sa.Column("priority", sa.String(length=20), nullable=True),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("result", sa.String(length=20), nullable=True),
        sa.Column("evidence", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["rule_id"], ["rule.id"]),
        sa.ForeignKeyConstraint(["scan_id"], ["scan.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_issue_scan_id"), "issue", ["scan_id"], unique=False)

    # 3. Revert scan table changes
    op.drop_column("scan", "skipped_count")
    op.alter_column("scan", "error_count", new_column_name="not_tested_count")
    op.add_column(
        "scan",
        sa.Column(
            "control_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
    )

    # Drop connection FKs
    op.drop_constraint("fk_scan_aws_connection_id", "scan", type_="foreignkey")
    op.drop_column("scan", "aws_connection_id")

    op.drop_constraint("fk_scan_gcp_connection_id", "scan", type_="foreignkey")
    op.drop_column("scan", "gcp_connection_id")

    op.drop_constraint("fk_scan_azure_connection_id", "scan", type_="foreignkey")
    op.drop_column("scan", "azure_connection_id")

    # Drop user_id
    op.drop_index(op.f("ix_scan_user_id"), table_name="scan")
    op.drop_constraint("fk_scan_user_id", "scan", type_="foreignkey")
    op.drop_column("scan", "user_id")

    # 4. Drop scan_result table
    op.drop_index(op.f("ix_scan_result_scan_id"), table_name="scan_result")
    op.drop_table("scan_result")

    # 5. Drop stub connection tables
    op.drop_table("aws_connection")
    op.drop_table("gcp_connection")
    op.drop_table("azure_connection")

    # 6. Drop platform table
    op.drop_table("platform")
