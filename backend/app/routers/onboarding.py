from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.job import GenerationJob
from app.models.garment import Garment
from app.services.credits import CreditService
from app.services.websocket import push_job_update

router = APIRouter()


class OnboardingGenerateRequest(BaseModel):
    photos: dict[str, str]  # { face: r2_key, profile: r2_key, fullbody: r2_key }
    garment_sku: str


@router.post("/generate")
async def onboarding_generate(
    body: OnboardingGenerateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a try-on during onboarding. Uses 1 free credit."""
    credit_service = CreditService(db)

    # Find garment by SKU
    result = await db.execute(
        select(Garment).where(Garment.sku == body.garment_sku, Garment.status == "active")
    )
    garment = result.scalar_one_or_none()

    if not garment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "GARMENT_NOT_FOUND", "message": "Garment not found for this SKU"},
        )

    async with db.begin():
        deducted = await credit_service.check_and_deduct(
            user.id, 1, "generation", description="Onboarding try-on"
        )
        if not deducted:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "code": "INSUFFICIENT_CREDITS",
                    "message": "Not enough credits.",
                },
            )

        job = GenerationJob(
            user_id=user.id,
            job_type="image",
            status="queued",
            garment_id=garment.id,
            input_params={
                "model_photo": list(body.photos.values())[0],  # Use first photo as model
                "garment_image": garment.image_url,
                "category": garment.category,
                "num_inference_steps": 30,
            },
            credits_used=1,
        )
        db.add(job)

    await db.refresh(job)

    # Enqueue Celery task
    from app.worker.celery_app import celery_app

    task = celery_app.send_task(
        "app.worker.tasks.generate_image.generate_tryon_image",
        args=[job.id],
        queue="default",
    )
    job.celery_task_id = task.id
    await db.commit()

    await push_job_update(user.id, job.id, "queued")

    return {"job_id": job.id}
