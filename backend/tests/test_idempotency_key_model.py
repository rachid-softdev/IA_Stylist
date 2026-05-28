"""Tests for idempotency_key column on GenerationJob model (H-05).

Introspection tests verifying:
- The idempotency_key column exists on the GenerationJob model
- The column allows NULL values
- The column has a unique constraint
"""
from app.models.job import GenerationJob


class TestIdempotencyKeyModel:

    def test_idempotency_key_column_exists(self):
        """GenerationJob must have an 'idempotency_key' column."""
        assert hasattr(GenerationJob, "idempotency_key"), (
            "GenerationJob model is missing the 'idempotency_key' column"
        )

    def test_idempotency_key_nullable(self):
        """The idempotency_key column must allow NULL values."""
        column = GenerationJob.__table__.columns["idempotency_key"]
        assert column.nullable is True, (
            "idempotency_key column should be nullable"
        )

    def test_idempotency_key_unique(self):
        """The idempotency_key column must have a unique constraint."""
        column = GenerationJob.__table__.columns["idempotency_key"]
        assert column.unique is True, (
            "idempotency_key column should be marked unique"
        )
