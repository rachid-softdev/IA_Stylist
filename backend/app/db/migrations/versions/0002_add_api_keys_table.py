"""add api_keys table

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-27
"""
import uuid
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "api_keys",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("brand_id", sa.String(36), sa.ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("key_hash", sa.String(255), nullable=False),
        sa.Column("prefix", sa.String(20), nullable=False, server_default="vfs_live_"),
        sa.Column("last_four", sa.String(4), nullable=False),
        sa.Column("name", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Migrate existing keys from brands table using parameterized query (safe from SQL injection)
    conn = op.get_bind()
    result = conn.execute(
        sa.text("SELECT id, api_key_hash FROM brands WHERE api_key_hash IS NOT NULL")
    )
    for row in result:
        op.execute(
            sa.text(
                "INSERT INTO api_keys (id, brand_id, key_hash, prefix, last_four, name, is_active) "
                "VALUES (:id, :brand_id, :key_hash, 'vfs_live_', '****', 'Migrated Key', true)"
            ).bindparams(
                id=str(uuid.uuid4()),
                brand_id=row.id,
                key_hash=row.api_key_hash,
            )
        )


def downgrade() -> None:
    op.drop_table("api_keys")
