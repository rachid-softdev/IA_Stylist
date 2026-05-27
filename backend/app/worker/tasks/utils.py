"""Utility functions for Celery task async execution."""
import asyncio


def run_async(coro):
    """Run an async coroutine safely, avoiding event loop conflicts.
    
    In Celery prefork workers, asyncio.run() can fail if there's already
    a running event loop. This utility handles both cases.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop — standard case
        return asyncio.run(coro)
    else:
        # A loop is already running — use run_until_complete
        return loop.run_until_complete(coro)
