"""add user role for admin console

Revision ID: 010
Revises: 009
"""
from alembic import op
import sqlalchemy as sa

revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("role", sa.String(length=20), nullable=False, server_default="user"),
    )
    op.create_index("ix_users_role", "users", ["role"], unique=False)


def downgrade():
    op.drop_index("ix_users_role", table_name="users")
    op.drop_column("users", "role")
