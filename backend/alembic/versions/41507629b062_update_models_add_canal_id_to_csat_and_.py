"""Update models: add canal_id to csat and ads, remove ignored fields from lifecycles

Revision ID: 41507629b062
Revises: initial
Create Date: 2026-04-08 10:57:30.907874

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

revision: str = "41507629b062"
down_revision: Union[str, None] = "initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add canal_id to csat table
    op.add_column("csat", sa.Column("canal_id", sa.Integer(), sa.ForeignKey("channels.id"), nullable=True))
    op.create_index("ix_csat_canal_id", "csat", ["canal_id"])

    # Add canal_id to ads table (replace ad_channel_id)
    op.add_column("ads", sa.Column("canal_id", sa.Integer(), sa.ForeignKey("channels.id"), nullable=True))
    op.create_index("ix_ads_canal_id", "ads", ["canal_id"])

    # Remove ignored fields from lifecycles
    op.drop_column("lifecycles", "pais")
    op.drop_column("lifecycles", "vendedor")
    op.drop_column("lifecycles", "canal")


def downgrade() -> None:
    # Remove canal_id from csat
    op.drop_index("ix_csat_canal_id", table_name="csat")
    op.drop_column("csat", "canal_id")

    # Remove canal_id from ads
    op.drop_index("ix_ads_canal_id", table_name="ads")
    op.drop_column("ads", "canal_id")

    # Add back ignored fields to lifecycles
    op.add_column("lifecycles", sa.Column("pais", sa.String(100), nullable=True))
    op.add_column("lifecycles", sa.Column("vendedor", sa.String(200), nullable=True))
    op.add_column("lifecycles", sa.Column("canal", sa.String(50), nullable=True))
