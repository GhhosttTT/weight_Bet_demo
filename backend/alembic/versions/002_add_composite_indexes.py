"""add composite indexes for query optimization

Revision ID: 002
Revises: 001
Create Date: 2024-01-15 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add composite indexes for optimizing queries"""
    
    # Create composite index on betting_plans (end_date, status)
    # This optimizes queries that check for expired plans
    # WHERE status = 'active' AND end_date < current_time
    op.create_index(
        'idx_betting_plans_end_date_status',
        'betting_plans',
        ['end_date', 'status']
    )
    
    # Create composite index on invitations (invitee_id, status)
    # This optimizes queries that fetch user's pending/viewed invitations
    # WHERE invitee_id = ? AND status IN ('pending', 'viewed')
    op.create_index(
        'idx_invitations_invitee_status',
        'invitations',
        ['invitee_id', 'status']
    )


def downgrade() -> None:
    """Drop composite indexes"""
    
    # Drop composite indexes
    op.drop_index('idx_invitations_invitee_status', table_name='invitations')
    op.drop_index('idx_betting_plans_end_date_status', table_name='betting_plans')
