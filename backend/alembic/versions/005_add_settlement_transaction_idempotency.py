"""add idempotency constraint for settlement transaction entries

Revision ID: 005
Revises: add_settlement_choices
"""
from alembic import op
import sqlalchemy as sa


revision = "005"
down_revision = "add_settlement_choices"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "uq_transactions_user_settlement_refund",
        "transactions",
        ["user_id", "related_settlement_id"],
        unique=True,
        sqlite_where=sa.text("type = 'REFUND'"),
        postgresql_where=sa.text("type = 'REFUND'"),
    )


def downgrade():
    op.drop_index("uq_transactions_user_settlement_refund", table_name="transactions")
