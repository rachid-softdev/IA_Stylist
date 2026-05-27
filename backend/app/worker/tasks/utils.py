"""Utility functions for Celery task async execution."""
import asyncio
import logging

logger = logging.getLogger(__name__)


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
        # A loop is already running — fire-and-forget via create_task
        logger.warning(
            "Event loop already running in Celery worker — "
            "scheduling coroutine as background task"
        )
        loop.create_task(coro)
