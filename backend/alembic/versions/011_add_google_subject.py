"""add Google OIDC subject to users

Revision ID: 011
Revises: 010
"""
from alembic import op
import sqlalchemy as sa

revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("google_subject", sa.String(length=255), nullable=True))
    op.create_index("ix_users_google_subject", "users", ["google_subject"], unique=True)


def downgrade():
    op.drop_index("ix_users_google_subject", table_name="users")
    op.drop_column("users", "google_subject")
