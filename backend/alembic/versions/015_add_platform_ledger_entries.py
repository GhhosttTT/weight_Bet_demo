"""add platform settlement fee ledger

Revision ID: 015
Revises: 014
"""
from alembic import op
import sqlalchemy as sa


revision = "015"
down_revision = "014"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "platform_ledger_entries",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "settlement_id",
            sa.String(length=36),
            sa.ForeignKey("settlements.id"),
            nullable=False,
        ),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("entry_type", sa.String(length=40), nullable=False, server_default="settlement_fee"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_platform_ledger_entries_id", "platform_ledger_entries", ["id"])
    op.create_index("ix_platform_ledger_entries_settlement_id", "platform_ledger_entries", ["settlement_id"], unique=True)


def downgrade():
    op.drop_index("ix_platform_ledger_entries_settlement_id", table_name="platform_ledger_entries")
    op.drop_index("ix_platform_ledger_entries_id", table_name="platform_ledger_entries")
    op.drop_table("platform_ledger_entries")
