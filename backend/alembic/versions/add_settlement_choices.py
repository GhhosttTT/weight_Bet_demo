"""add settlement choices table and arbitration fields to settlements

Revision ID: add_settlement_choices
Revises: previous_revision_id
Create Date: 2026-03-25

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_settlement_choices'
down_revision = 'previous_revision_id'
branch_labels = None
depends_on = None


def upgrade():
    # Create settlement_choices table
    op.create_table('settlement_choices',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('plan_id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('self_achieved', sa.Boolean(), nullable=False),
        sa.Column('opponent_achieved', sa.Boolean(), nullable=False),
        sa.Column('round', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_settlement_choices_plan_id'), 'settlement_choices', ['plan_id'], unique=False)
    op.create_index(op.f('ix_settlement_choices_user_id'), 'settlement_choices', ['user_id'], unique=False)
    op.create_index(op.f('ix_settlement_choices_id'), 'settlement_choices', ['id'], unique=False)
    
    # Add arbitration fields to settlements table
    op.add_column('settlements', sa.Column('in_arbitration', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('settlements', sa.Column('arbitration_fee', sa.Float(), nullable=True))


def downgrade():
    # Remove arbitration fields from settlements table
    op.drop_column('settlements', 'arbitration_fee')
    op.drop_column('settlements', 'in_arbitration')
    
    # Drop indexes
    op.drop_index(op.f('ix_settlement_choices_id'), table_name='settlement_choices')
    op.drop_index(op.f('ix_settlement_choices_user_id'), table_name='settlement_choices')
    op.drop_index(op.f('ix_settlement_choices_plan_id'), table_name='settlement_choices')
    
    # Drop settlement_choices table
    op.drop_table('settlement_choices')
