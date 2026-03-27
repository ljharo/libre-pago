"""create_users_table

Revision ID: 3e573c70d2aa
Revises: a9368b077657
Create Date: 2026-03-26 16:12:43.510316

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

revision: str = "3e573c70d2aa"
down_revision: Union[str, None] = "a9368b077657"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=50), autoincrement=False, nullable=False),
        sa.Column("password_hash", sa.String(length=255), autoincrement=False, nullable=False),
        sa.Column("role", sa.String(length=20), autoincrement=False, nullable=True),
        sa.Column("created_at", sa.DateTime(), autoincrement=False, nullable=True),
        sa.Column("updated_at", sa.DateTime(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="users_pkey"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
