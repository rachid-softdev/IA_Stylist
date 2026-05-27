import logging
from app.worker.celery_app import celery_app
from app.worker.tasks.utils import run_async

logger = logging.getLogger(__name__)


@celery_app.task
def cleanup_temp_files():
    """Periodic task: clean up temporary uploads older than 24h."""
    logger.warning("TODO: cleanup_temp_files not yet implemented")

    async def _run():
        from datetime import datetime, timedelta
        from app.services.storage import delete_file

        cutoff = datetime.utcnow() - timedelta(hours=24)
        # In production: query DB for old uploads and delete from R2
        pass

    run_async(_run())


@celery_app.task
def cleanup_old_jobs():
    """Periodic task: clean up old job results based on plan retention."""

    async def _run():
        from datetime import datetime, timedelta
        from app.worker.tasks.generate_image import AsyncSessionLocal, GenerationJob, select

        # Delete jobs older than retention period
        async with AsyncSessionLocal() as db:
            cutoff = datetime.utcnow() - timedelta(days=30)
            result = await db.execute(
                select(GenerationJob).where(GenerationJob.created_at < cutoff)
            )
            old_jobs = result.scalars().all()
            for job in old_jobs:
                await db.delete(job)
            await db.commit()

    run_async(_run())
