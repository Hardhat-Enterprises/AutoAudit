"""Add evidence validation table (int PK + user FK).

Revision ID: f6c7d8e9f012
Revises: d4e5f6g7h890
Create Date: 2025-12-21
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "f6c7d8e9f012"
down_revision: Union[str, Sequence[str], None] = "d4e5f6g7h890"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "evidence_validation",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
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


