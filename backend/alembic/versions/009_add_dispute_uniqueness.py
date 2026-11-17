"""create disputes table and enforce one dispute per settlement participant

Revision ID: 009
Revises: 008
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    if not inspect(bind).has_table("disputes"):
        dispute_status = sa.Enum(
            "pending", "under_review", "resolved", "rejected",
            name="disputestatus",
        )
        op.create_table(
            "disputes",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("settlement_id", sa.String(length=36), nullable=False),
            sa.Column("user_id", sa.String(length=36), nullable=False),
            sa.Column("reason", sa.Text(), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column(
                "status", dispute_status,
                nullable=False, server_default="pending",
            ),
            sa.Column("admin_notes", sa.Text(), nullable=True),
            sa.Column("resolved_by", sa.String(length=36), nullable=True),
            sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["settlement_id"], ["settlements.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "settlement_id", "user_id",
                name="uq_dispute_settlement_user",
            ),
        )
        op.create_index("ix_disputes_id", "disputes", ["id"], unique=False)
        op.create_index("ix_disputes_settlement_id", "disputes", ["settlement_id"], unique=False)
        op.create_index("ix_disputes_user_id", "disputes", ["user_id"], unique=False)
    else:
        with op.batch_alter_table("disputes") as batch_op:
            batch_op.create_unique_constraint(
                "uq_dispute_settlement_user",
                ["settlement_id", "user_id"],
            )


def downgrade():
    with op.batch_alter_table("disputes") as batch_op:
        batch_op.drop_constraint(
            "uq_dispute_settlement_user",
            type_="unique",
        )
