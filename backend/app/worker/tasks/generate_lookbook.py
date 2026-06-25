from app.worker.celery_app import celery_app
from app.worker.tasks.utils import run_async


@celery_app.task(bind=True, max_retries=1)
def generate_lookbook(self, job_id: str):
    """Generate a batch lookbook for a collection of garments."""

    async def _run():
        from app.worker.tasks.generate_image import _update_job_status, _is_cancelled, AsyncSessionLocal, GenerationJob, select
        from app.services.websocket import push_job_update

        await _update_job_status(job_id, "processing")

        # Cooperative cancellation check
        if await _is_cancelled(job_id):
            return

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(GenerationJob).where(GenerationJob.id == job_id))
            job = result.scalar_one_or_none()

            if not job:
                return

            garment_ids = job.input_params.get("garment_ids", [])
            style = job.input_params.get("style", "studio")

            # In production: loop through garment_ids, generate try-ons,
            # compile into lookbook (PDF/ZIP), store in R2

            job.status = "done"
            job.ai_provider = "batch"
            await db.commit()

            await push_job_update(
                user_id=job.user_id,
                job_id=job_id,
                status="done",
            )

    run_async(_run())
