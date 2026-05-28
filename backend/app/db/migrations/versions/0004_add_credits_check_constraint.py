"""add credits >= 0 check constraint

Revision ID: 0004
Revises: 0003
Create Date: 2026-05-28
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Fix any negative credits first
    conn = op.get_bind()
    conn.execute(sa.text("UPDATE users SET credits = 0 WHERE credits < 0"))
    # Add CHECK constraint
    op.create_check_constraint(
        "ck_users_credits_non_negative",
        "users",
        sa.text("credits >= 0"),
    )


def downgrade() -> None:
    op.drop_constraint("ck_users_credits_non_negative", "users", type_="check")
