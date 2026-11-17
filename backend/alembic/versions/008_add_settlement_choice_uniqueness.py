"""enforce one settlement choice per user and round

Revision ID: 008
Revises: 007
"""
from alembic import op


revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("settlement_choices") as batch_op:
        batch_op.create_unique_constraint(
            "uq_settlement_choice_plan_user_round",
            ["plan_id", "user_id", "round"],
        )


def downgrade():
    with op.batch_alter_table("settlement_choices") as batch_op:
        batch_op.drop_constraint(
            "uq_settlement_choice_plan_user_round",
            type_="unique",
        )
