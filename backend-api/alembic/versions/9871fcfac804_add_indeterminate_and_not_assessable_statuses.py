"""Add indeterminate and not_assessable scan result statuses.

Adds the two statuses to a CHECK on scan_result.status and their counts
to scan. Neither counts toward compliance_score.

Revision ID: 9871fcfac804
Revises: e5f6a7b8c9d0
Create Date: 2026-11-18
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9871fcfac804"
down_revision: Union[str, Sequence[str], None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "scan",
        sa.Column(
            "indeterminate_count", sa.Integer(), nullable=False, server_default="0"
        ),
    )
    op.add_column(
        "scan",
        sa.Column(
            "not_assessable_count", sa.Integer(), nullable=False, server_default="0"
        ),
    )
    op.create_check_constraint(
        "ck_scan_result_status",
        "scan_result",
        "status IN ('pending', 'passed', 'failed', 'indeterminate', "
        "'not_assessable', 'error', 'skipped')",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("ck_scan_result_status", "scan_result", type_="check")
    op.drop_column("scan", "not_assessable_count")
    op.drop_column("scan", "indeterminate_count")
