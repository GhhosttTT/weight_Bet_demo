"""add Stripe Connect account and payout references

Revision ID: 012
Revises: 011
"""
from alembic import op
import sqlalchemy as sa

revision = "012"
down_revision = "011"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("stripe_account_id", sa.String(length=255), nullable=True))
    op.create_index("ix_users_stripe_account_id", "users", ["stripe_account_id"], unique=True)
    op.add_column("transactions", sa.Column("external_payment_id", sa.String(length=255), nullable=True))
    op.add_column("transactions", sa.Column("external_transfer_id", sa.String(length=255), nullable=True))
    op.create_index("ix_transactions_external_payment_id", "transactions", ["external_payment_id"], unique=True)
    op.create_index("ix_transactions_external_transfer_id", "transactions", ["external_transfer_id"], unique=True)


def downgrade():
    op.drop_index("ix_transactions_external_transfer_id", table_name="transactions")
    op.drop_index("ix_transactions_external_payment_id", table_name="transactions")
    op.drop_column("transactions", "external_transfer_id")
    op.drop_column("transactions", "external_payment_id")
    op.drop_index("ix_users_stripe_account_id", table_name="users")
    op.drop_column("users", "stripe_account_id")
