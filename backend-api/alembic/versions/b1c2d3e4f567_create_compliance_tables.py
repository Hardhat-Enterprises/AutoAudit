"""Create compliance tables

Revision ID: b1c2d3e4f567
Revises: a0ffaa05246a
Create Date: 2025-11-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'b1c2d3e4f567'
down_revision: Union[str, Sequence[str], None] = 'a0ffaa05246a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create compliance-related tables."""
    # Create tenant table
    op.create_table('tenant',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('external_tenant_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create rule table
    op.create_table('rule',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('framework', sa.String(length=100), nullable=False),
        sa.Column('control_key', sa.String(length=100), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create scan table
    op.create_table('scan',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='running'),
        sa.Column('compliance_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('total_controls', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('passed_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failed_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('not_tested_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenant.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scan_tenant_id'), 'scan', ['tenant_id'], unique=False)

    # Create issue table
    op.create_table('issue',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('scan_id', sa.Integer(), nullable=False),
        sa.Column('rule_id', sa.Integer(), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('result', sa.String(length=20), nullable=True),
        sa.Column('evidence', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['rule_id'], ['rule.id'], ),
        sa.ForeignKeyConstraint(['scan_id'], ['scan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_issue_scan_id'), 'issue', ['scan_id'], unique=False)


def downgrade() -> None:
    """Drop compliance-related tables."""
    op.drop_index(op.f('ix_issue_scan_id'), table_name='issue')
    op.drop_table('issue')
    op.drop_index(op.f('ix_scan_tenant_id'), table_name='scan')
    op.drop_table('scan')
    op.drop_table('rule')
    op.drop_table('tenant')
