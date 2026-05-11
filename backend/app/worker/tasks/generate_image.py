import time
from celery import Task
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from app.config import get_settings
from app.models.job import GenerationJob
from app.services.websocket import push_job_update
from app.worker.celery_app import celery_app

settings = get_settings()

# Create a sync-ish DB session for Celery tasks
engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def _update_job_status(job_id: str, status: str, error_message: str | None = None):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(GenerationJob).where(GenerationJob.id == job_id))
        job = result.scalar_one_or_none()
        if job:
            job.status = status
            if error_message:
                job.error_message = error_message
            if status in ("done", "error"):
                job.completed_at = time.time()
            await db.commit()

            await push_job_update(
                user_id=job.user_id,
                job_id=job_id,
                status=status,
                error_message=error_message,
            )


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def generate_tryon_image(self, job_id: str):
    """Generate a try-on image using AI services."""
    import asyncio

    async def _run():
        await _update_job_status(job_id, "processing")

        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(GenerationJob).where(GenerationJob.id == job_id))
                job = result.scalar_one_or_none()

                if not job:
                    return

                # Call AI service
                from app.services.ai.router import AIRouter

                router = AIRouter()
                result_url, provider = await router.generate_tryon(
                    model_photo=job.input_params.get("model_photo", ""),
                    garment_image=job.input_params.get("garment_image", ""),
                    category=job.input_params.get("category", "top"),
                    steps=job.input_params.get("num_inference_steps", 30),
                    seed=job.input_params.get("seed"),
                )

                # Update job
                job.status = "done"
                job.result_url = result_url
                job.ai_provider = provider
                job.completed_at = time.time()

                await db.commit()

                await push_job_update(
                    user_id=job.user_id,
                    job_id=job_id,
                    status="done",
                    result_url=result_url,
                )

        except Exception as exc:
            # Retry logic
            if self.request.retries < self.max_retries:
                raise self.retry(exc=exc)

            # Final failure — update status and refund
            await _update_job_status(job_id, "error", str(exc))

            async with AsyncSessionLocal() as db:
                from app.services.credits import CreditService

                result = await db.execute(select(GenerationJob).where(GenerationJob.id == job_id))
                job = result.scalar_one_or_none()
                if job:
                    credit_service = CreditService(db)
                    await credit_service.refund(
                        job.user_id, job.credits_used, "refund", job.id, f"Job failed: {str(exc)}"
                    )

    asyncio.run(_run())
