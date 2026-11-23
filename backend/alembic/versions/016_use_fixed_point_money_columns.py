"""store monetary values as fixed-point decimals

Revision ID: 016
Revises: 015
"""
from alembic import context, op
import sqlalchemy as sa


revision = "016"
down_revision = "015"
branch_labels = None
depends_on = None


MONEY_COLUMNS = (
    ("balances", "available_balance", False),
    ("balances", "frozen_balance", False),
    ("betting_plans", "bet_amount", False),
    ("transactions", "amount", False),
    ("settlements", "creator_amount", False),
    ("settlements", "participant_amount", False),
    ("settlements", "platform_fee", False),
    ("settlements", "arbitration_fee", True),
    ("platform_ledger_entries", "amount", False),
)


def _fixed_point_type():
    return sa.Numeric(12, 2)


def _alter(table, column, nullable, existing_type, target_type):
    dialect = context.get_context().dialect.name
    kwargs = {
        "existing_type": existing_type,
        "type_": target_type,
        "existing_nullable": nullable,
    }
    if dialect == "postgresql":
        if isinstance(target_type, sa.Numeric):
            kwargs["postgresql_using"] = f"ROUND({column}::numeric, 2)"
        else:
            kwargs["postgresql_using"] = f"{column}::double precision"
        op.alter_column(table, column, **kwargs)
    elif dialect == "sqlite":
        # SQLite cannot ALTER COLUMN directly; batch mode recreates the table
        # while preserving foreign keys, indexes, defaults, and constraints.
        with op.batch_alter_table(table) as batch:
            batch.alter_column(column, **kwargs)
    else:
        op.alter_column(table, column, **kwargs)


def upgrade():
    for table, column, nullable in MONEY_COLUMNS:
        _alter(table, column, nullable, sa.Float(), _fixed_point_type())


def downgrade():
    for table, column, nullable in reversed(MONEY_COLUMNS):
        _alter(table, column, nullable, _fixed_point_type(), sa.Float())
