from celery import Celery
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "vfs",
    broker=settings.CELERY_BROKER_URL or settings.REDIS_URL,
    backend=settings.CELERY_RESULT_BACKEND or settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_default_queue="default",
    task_queues={
        "high": {"exchange": "high", "routing_key": "high"},
        "default": {"exchange": "default", "routing_key": "default"},
        "low": {"exchange": "low", "routing_key": "low"},
    },
    task_routes={
        "app.worker.tasks.generate_video.*": {"queue": "high"},
        "app.worker.tasks.generate_image.*": {"queue": "default"},
        "app.worker.tasks.cleanup.*": {"queue": "low"},
        "app.worker.tasks.generate_lookbook.*": {"queue": "low"},
    },
    # ⚠️ CRITICAL: Credits are deducted in the API handler, NOT in Celery tasks.
    # If deduction logic is ever moved into a worker, the idempotency_key column
    # on GenerationJob MUST be used to prevent double-deduction on retries.
    # See backend/app/models/job.py for the idempotency_key field.
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=60,
    task_max_retries=3,
)

celery_app.autodiscover_tasks(
    ["app.worker.tasks.generate_image", "app.worker.tasks.generate_video", "app.worker.tasks.cleanup", "app.worker.tasks.generate_lookbook"]
)
