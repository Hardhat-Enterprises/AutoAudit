"""Make evidence_validation use int PK and user_id FK.

Revision ID: f6c7d8e9f012
Revises: e5b1c9d8a7f0
Create Date: 2025-12-20
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "f6c7d8e9f012"
down_revision: Union[str, Sequence[str], None] = "e5b1c9d8a7f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create a new table with the desired schema. We keep user_id nullable during
    # the data migration step, then enforce NOT NULL once we backfill.
    op.create_table(
        "evidence_validation_new",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("strategy_name", sa.String(length=255), nullable=False),
        sa.Column("source_filename", sa.String(length=512), nullable=True),
        sa.Column("text_hash", sa.String(length=64), nullable=True),
        sa.Column("extracted_text_encrypted", sa.Text(), nullable=True),
        sa.Column("matches_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "status", sa.String(length=25), server_default="success", nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Best-effort migrate existing rows. Old user_id was a string; if it looks like
    # an integer, cast it, otherwise temporarily set NULL.
    op.execute(
        """
        INSERT INTO evidence_validation_new (
            created_at,
            user_id,
            strategy_name,
            source_filename,
            text_hash,
            extracted_text_encrypted,
            matches_json,
            status
        )
        SELECT
            created_at,
            CASE
                WHEN user_id ~ '^[0-9]+$' THEN user_id::integer
                ELSE NULL
            END AS user_id,
            strategy_name,
            source_filename,
            text_hash,
            extracted_text_encrypted,
            matches_json,
            status
        FROM evidence_validation
        """
    )

    # Backfill any missing user_id to the first available user (consistent with
    # scan.user_id migration in d4e5f6g7h890).
    op.execute(
        """
        UPDATE evidence_validation_new
        SET user_id = (SELECT id FROM "user" LIMIT 1)
        WHERE user_id IS NULL
        """
    )

    # Enforce NOT NULL now that we've backfilled.
    op.alter_column("evidence_validation_new", "user_id", nullable=False)

    # Replace the old table.
    op.drop_table("evidence_validation")
    op.rename_table("evidence_validation_new", "evidence_validation")

    # Add FK + indexes on the final table name.
    op.create_foreign_key(
        "fk_evidence_validation_user_id",
        "evidence_validation",
        "user",
        ["user_id"],
        ["id"],
    )
    op.create_index(
        op.f("ix_evidence_validation_created_at"),
        "evidence_validation",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_evidence_validation_user_id"),
        "evidence_validation",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_evidence_validation_user_id"), table_name="evidence_validation")
    op.drop_index(
        op.f("ix_evidence_validation_created_at"), table_name="evidence_validation"
    )
    op.drop_constraint(
        "fk_evidence_validation_user_id",
        "evidence_validation",
        type_="foreignkey",
    )
    op.drop_table("evidence_validation")

    # Recreate the original schema (UUID/string PK + user_id string).
    op.create_table(
        "evidence_validation",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("strategy_name", sa.String(length=255), nullable=False),
        sa.Column("source_filename", sa.String(length=512), nullable=True),
        sa.Column("text_hash", sa.String(length=64), nullable=True),
        sa.Column("extracted_text_encrypted", sa.Text(), nullable=True),
        sa.Column("matches_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "status", sa.String(length=20), server_default="success", nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_evidence_validation_created_at"),
        "evidence_validation",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_evidence_validation_user_id"),
        "evidence_validation",
        ["user_id"],
        unique=False,
    )


