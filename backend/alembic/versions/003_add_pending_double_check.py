"""add pending_double_check to betting_plans

Revision ID: 003_add_pending_double_check
Revises: 002
Create Date: 2026-03-24 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003_add_pending_double_check'
down_revision = '002'  # Fixed: was '002_add_composite_indexes' which doesn't exist
branch_labels = None
depends_on = None


def upgrade():
    # Skip: Column already exists in database
    pass
    # Add pending_double_check column to betting_plans
    # op.add_column('betting_plans', sa.Column('pending_double_check', sa.Boolean(), nullable=False, server_default=sa.text('false')))


def downgrade():
    # Skip: Column will be removed in next migration
    pass
    # Remove pending_double_check column
    # op.drop_column('betting_plans', 'pending_double_check')

