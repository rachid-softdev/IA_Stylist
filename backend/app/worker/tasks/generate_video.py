import time
from app.worker.celery_app import celery_app
from app.worker.tasks.utils import run_async


@celery_app.task(bind=True, max_retries=1, default_retry_delay=60)
def generate_video(self, job_id: str):
    """Generate a fashion video from try-on result."""

    async def _run():
        from app.worker.tasks.generate_image import _update_job_status, AsyncSessionLocal, GenerationJob, select
        from app.services.websocket import push_job_update

        await _update_job_status(job_id, "processing")

        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(GenerationJob).where(GenerationJob.id == job_id))
                job = result.scalar_one_or_none()

                if not job:
                    return

                from app.services.ai.kling_client import KlingClient

                client = KlingClient()
                result_url = await client.generate_video(
                    image_url=job.input_params.get("source_job_id", ""),
                    video_type=job.input_params.get("video_type", "runway_walk"),
                )

                job.status = "done"
                job.result_url = result_url
                job.ai_provider = "kling"
                job.completed_at = time.time()
                await db.commit()

                await push_job_update(
                    user_id=job.user_id,
                    job_id=job_id,
                    status="done",
                    result_url=result_url,
                )

        except Exception as exc:
            if self.request.retries < self.max_retries:
                raise self.retry(exc=exc)

            await _update_job_status(job_id, "error", str(exc))

    run_async(_run())
