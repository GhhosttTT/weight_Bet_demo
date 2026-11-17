"""persist current settlement choice round

Revision ID: 007
Revises: 006
"""
from alembic import op
import sqlalchemy as sa


revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("betting_plans") as batch_op:
        batch_op.add_column(
            sa.Column("settlement_round", sa.Integer(), nullable=False, server_default="1")
        )


def downgrade():
    with op.batch_alter_table("betting_plans") as batch_op:
        batch_op.drop_column("settlement_round")
