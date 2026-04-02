"""remove pending_double_check field

Revision ID: 004
Revises: 003_add_pending_double_check
Create Date: 2026-04-02

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003_add_pending_double_check'  # Fixed to match full revision name
branch_labels = None
depends_on = None


def upgrade():
    # Remove pending_double_check column from betting_plans table
    with op.batch_alter_table('betting_plans', schema=None) as batch_op:
        batch_op.drop_column('pending_double_check')


def downgrade():
    # Add back the column for rollback
    with op.batch_alter_table('betting_plans', schema=None) as batch_op:
        batch_op.add_column(sa.Column('pending_double_check', sa.Boolean(), server_default='false', nullable=False))
