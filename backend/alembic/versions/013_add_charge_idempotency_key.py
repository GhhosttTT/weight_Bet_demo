"""add charge idempotency key

Revision ID: 013
Revises: 012
"""
from alembic import op
import sqlalchemy as sa

revision = "013"
down_revision = "012"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("transactions", sa.Column("idempotency_key", sa.String(length=255), nullable=True))
    op.create_index("ix_transactions_idempotency_key", "transactions", ["idempotency_key"], unique=True)


def downgrade():
    op.drop_index("ix_transactions_idempotency_key", table_name="transactions")
    op.drop_column("transactions", "idempotency_key")
