"""create invitations table

Revision ID: 001
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create invitations table with all constraints and indexes"""
    
    # Create invitations table
    op.create_table(
        'invitations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('plan_id', sa.String(length=36), nullable=False),
        sa.Column('inviter_id', sa.String(length=36), nullable=False),
        sa.Column('invitee_email', sa.String(length=255), nullable=False),
        sa.Column('invitee_id', sa.String(length=36), nullable=True),
        sa.Column(
            'status',
            sa.Enum('pending', 'viewed', 'accepted', 'rejected', 'expired', name='invitationstatus'),
            nullable=False,
            server_default='pending'
        ),
        sa.Column('sent_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('viewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
        
        # Primary key
        sa.PrimaryKeyConstraint('id', name='pk_invitations'),
        
        # Foreign keys
        sa.ForeignKeyConstraint(['plan_id'], ['betting_plans.id'], name='fk_invitations_plan_id'),
        sa.ForeignKeyConstraint(['inviter_id'], ['users.id'], name='fk_invitations_inviter_id'),
        sa.ForeignKeyConstraint(['invitee_id'], ['users.id'], name='fk_invitations_invitee_id'),
        
        # Unique constraint - one invitation per plan
        sa.UniqueConstraint('plan_id', name='uq_invitations_plan_id'),
        
        # Check constraint for status values
        sa.CheckConstraint(
            "status IN ('pending', 'viewed', 'accepted', 'rejected', 'expired')",
            name='check_invitation_status'
        )
    )
    
    # Create indexes
    op.create_index('ix_invitations_id', 'invitations', ['id'])
    op.create_index('ix_invitations_plan_id', 'invitations', ['plan_id'])
    op.create_index('ix_invitations_inviter_id', 'invitations', ['inviter_id'])
    op.create_index('ix_invitations_invitee_email', 'invitations', ['invitee_email'])
    op.create_index('ix_invitations_invitee_id', 'invitations', ['invitee_id'])
    op.create_index('ix_invitations_status', 'invitations', ['status'])
    
    # Add new columns to betting_plans table
    op.add_column('betting_plans', sa.Column('abandoned_by', sa.String(length=36), nullable=True))
    op.add_column('betting_plans', sa.Column('abandoned_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('betting_plans', sa.Column('expiry_checked_at', sa.DateTime(timezone=True), nullable=True))
    
    # Add foreign key for abandoned_by
    op.create_foreign_key(
        'fk_betting_plans_abandoned_by',
        'betting_plans',
        'users',
        ['abandoned_by'],
        ['id']
    )
    
    # Update PlanStatus enum to include 'expired' status
    # Note: For PostgreSQL, we need to add the new value to the existing enum
    # For SQLite, enums are stored as strings so no migration needed
    # This is a PostgreSQL-specific operation
    op.execute("ALTER TYPE planstatus ADD VALUE IF NOT EXISTS 'expired'")


def downgrade() -> None:
    """Drop invitations table and revert betting_plans changes"""
    
    # Drop indexes
    op.drop_index('ix_invitations_status', table_name='invitations')
    op.drop_index('ix_invitations_invitee_id', table_name='invitations')
    op.drop_index('ix_invitations_invitee_email', table_name='invitations')
    op.drop_index('ix_invitations_inviter_id', table_name='invitations')
    op.drop_index('ix_invitations_plan_id', table_name='invitations')
    op.drop_index('ix_invitations_id', table_name='invitations')
    
    # Drop invitations table
    op.drop_table('invitations')
    
    # Drop enum type (PostgreSQL only)
    op.execute("DROP TYPE IF EXISTS invitationstatus")
    
    # Remove columns from betting_plans
    op.drop_constraint('fk_betting_plans_abandoned_by', 'betting_plans', type_='foreignkey')
    op.drop_column('betting_plans', 'expiry_checked_at')
    op.drop_column('betting_plans', 'abandoned_at')
    op.drop_column('betting_plans', 'abandoned_by')
    
    # Note: Removing 'expired' from PlanStatus enum is complex in PostgreSQL
    # and typically not recommended. If needed, it requires creating a new enum
    # type and migrating data.
