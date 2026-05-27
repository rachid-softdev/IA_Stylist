"""Tests for Celery task async execution utilities."""
import asyncio
import pytest
from app.worker.tasks.utils import run_async


@pytest.mark.asyncio
async def test_run_async_basic():
    """run_async must execute a coroutine and return result from sync context."""
    async def dummy():
        return 42

    # run_async is not async — call it directly inside a sync wrapper
    def _sync_run():
        return run_async(dummy())

    # We're already in async context (pytest-asyncio)
    # So this will hit the 'else' branch (running loop) — fire-and-forget
    # In production (Celery workers), it's sync and will use asyncio.run()
    # This test verifies it doesn't crash
    result = _sync_run()
    # In async context, run_async returns None (fire-and-forget)
    # In sync context, it would return 42
    assert result is None  # fire-and-forget from async context


def test_run_async_sync_context():
    """run_async must work from sync context (simulating Celery worker)."""
    async def dummy():
        return 42

    # Create a new event loop for this sync test
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = run_async(dummy())
        assert result == 42
    finally:
        loop.close()
        asyncio.set_event_loop(None)
