"""Create users, search_history, favorites tables

Revision ID: 0001
Revises:
Create Date: 2026-07-04 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("username", sa.String(), unique=True, index=True, nullable=False),
        sa.Column("email", sa.String(), unique=True, index=True, nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True),
    )
    op.create_table(
        "search_history",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("city_name", sa.String(), nullable=False),
        sa.Column("country", sa.String()),
        sa.Column("travel_score", sa.Float()),
        sa.Column("timestamp", sa.DateTime()),
    )
    op.create_table(
        "favorites",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("city_name", sa.String(), nullable=False),
        sa.Column("country", sa.String()),
        sa.Column("lat", sa.Float()),
        sa.Column("lon", sa.Float()),
        sa.Column("created_at", sa.DateTime()),
    )


def downgrade() -> None:
    op.drop_table("favorites")
    op.drop_table("search_history")
    op.drop_table("users")
