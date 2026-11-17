"""fix SQLite-safe default for settlement arbitration flag

Revision ID: 006
Revises: 005
"""
from alembic import op
import sqlalchemy as sa


revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("settlements") as batch_op:
        batch_op.alter_column(
            "in_arbitration",
            existing_type=sa.Boolean(),
            existing_nullable=False,
            server_default=sa.false(),
        )


def downgrade():
    with op.batch_alter_table("settlements") as batch_op:
        batch_op.alter_column(
            "in_arbitration",
            existing_type=sa.Boolean(),
            existing_nullable=False,
            server_default=sa.text("'false'"),
        )
