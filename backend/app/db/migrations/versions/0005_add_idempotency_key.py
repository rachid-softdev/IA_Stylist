"""add idempotency_key to generation_jobs

Revision ID: 0005
Revises: 0004
Create Date: 2026-05-28
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "generation_jobs",
        sa.Column("idempotency_key", sa.String(64), nullable=True, unique=True, index=True),
    )


def downgrade() -> None:
    op.drop_column("generation_jobs", "idempotency_key")
