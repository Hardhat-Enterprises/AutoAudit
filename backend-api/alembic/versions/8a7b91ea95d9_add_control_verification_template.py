"""add control verification template
 
Revision ID: 8a7b91ea95d9
Revises: j1k2l3m4n567
Create Date: 2026-05-08 09:22:25.327975
 
"""
from typing import Sequence, Union
 
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
 
# revision identifiers, used by Alembic.
revision: str = '8a7b91ea95d9'
down_revision: Union[str, Sequence[str], None] = 'j1k2l3m4n567'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
 
 
def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'control_verification_template',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('framework', sa.String(length=50), nullable=False),
        sa.Column('benchmark', sa.String(length=100), nullable=False),
        sa.Column('version', sa.String(length=20), nullable=False),
        sa.Column('control_id', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('instructions', sa.Text(), nullable=False),
        sa.Column('keywords', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('evidence_type', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'framework',
            'benchmark',
            'version',
            'control_id',
            name='uq_template_framework_benchmark_version_control',
        ),
    )
    op.create_index(
        op.f('ix_control_verification_template_control_id'),
        'control_verification_template',
        ['control_id'],
        unique=False,
    )
 
 
def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f('ix_control_verification_template_control_id'),
        table_name='control_verification_template',
    )
    op.drop_table('control_verification_template')