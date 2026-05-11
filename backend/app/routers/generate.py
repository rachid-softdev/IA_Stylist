from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional

from app.dependencies import get_current_user, get_current_brand_admin
from app.db.session import get_db
from app.models.user import User
from app.models.job import GenerationJob
from app.models.garment import Garment
from app.services.credits import CreditService
from app.services.websocket import push_job_update
from app.schemas.common import (
    GenerateTryOnRequest,
    GenerateVideoRequest,
    GenerateLookbookRequest,
    JobCreateResponse,
    JobResponse,
)

router = APIRouter()


@router.post("/try-on", response_model=JobCreateResponse)
async def create_try_on(
    body: GenerateTryOnRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create an image try-on generation job."""
    credit_service = CreditService(db)

    # Check credits
    has_credits = await credit_service.check_and_reserve(user.id, 1)
    if not has_credits:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "code": "INSUFFICIENT_CREDITS",
                "message": "Not enough credits. Please upgrade your plan.",
            },
        )

    # Deduct credits (pending — will be confirmed or refunded after job)
    deducted = await credit_service.deduct(
        user.id, 1, "generation", description="Try-On Image"
    )
    if not deducted:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={"code": "INSUFFICIENT_CREDITS", "message": "Not enough credits"},
        )

    # Validate garment if from catalog
    if body.garment_id:
        result = await db.execute(select(Garment).where(Garment.id == body.garment_id))
        garment = result.scalar_one_or_none()
        if not garment:
            # Refund if garment not found
            await credit_service.refund(user.id, 1, "refund", description="Garment not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "GARMENT_NOT_FOUND", "message": "Garment not found"},
            )
        body.garment_image = garment.image_url

    # Create job in DB
    job = GenerationJob(
        user_id=user.id,
        job_type="image",
        status="queued",
        garment_id=body.garment_id,
        input_params={
            "model_photo": body.model_photo_id,
            "garment_image": body.garment_image,
            "category": body.category,
            "num_inference_steps": body.num_inference_steps,
            "seed": body.seed,
        },
        credits_used=1,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Enqueue Celery task
    from app.worker.celery_app import celery_app

    celery_app.send_task(
        "app.worker.tasks.generate_image.generate_tryon_image",
        args=[job.id],
        queue="default",
    )

    await push_job_update(user.id, job.id, "queued")

    return JobCreateResponse(job_id=job.id)


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a generation job status and result."""
    result = await db.execute(
        select(GenerationJob).where(
            GenerationJob.id == job_id,
            GenerationJob.user_id == user.id,
        )
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "JOB_NOT_FOUND", "message": "Job not found"},
        )

    return job


@router.get("/jobs")
async def list_jobs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's generation jobs."""
    query = select(GenerationJob).where(GenerationJob.user_id == user.id)

    if status_filter:
        query = query.where(GenerationJob.status == status_filter)

    query = query.order_by(desc(GenerationJob.created_at))

    # Get total
    count_result = await db.execute(
        select(GenerationJob).where(GenerationJob.user_id == user.id)
    )
    total = len(count_result.scalars().all())

    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    jobs = result.scalars().all()

    return {
        "data": jobs,
        "meta": {"page": page, "page_size": page_size, "total": total},
    }


@router.post("/video", response_model=JobCreateResponse)
async def create_video(
    body: GenerateVideoRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a video generation job (3 credits)."""
    credit_service = CreditService(db)

    has_credits = await credit_service.check_and_reserve(user.id, 3)
    if not has_credits:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={"code": "INSUFFICIENT_CREDITS", "message": "Not enough credits for video"},
        )

    deducted = await credit_service.deduct(user.id, 3, "generation", description="Video generation")
    if not deducted:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED)

    job = GenerationJob(
        user_id=user.id,
        job_type="video",
        status="queued",
        input_params={"video_type": body.video_type, "source_job_id": body.job_id},
        credits_used=3,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    from app.worker.celery_app import celery_app

    celery_app.send_task(
        "app.worker.tasks.generate_video.generate_video",
        args=[job.id],
        queue="high",
    )

    return JobCreateResponse(job_id=job.id)


@router.post("/lookbook", response_model=JobCreateResponse)
async def create_lookbook(
    body: GenerateLookbookRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a lookbook generation job (batch)."""
    credits_needed = len(body.garment_ids)
    credit_service = CreditService(db)

    has_credits = await credit_service.check_and_reserve(user.id, credits_needed)
    if not has_credits:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={"code": "INSUFFICIENT_CREDITS", "message": "Not enough credits for lookbook"},
        )

    await credit_service.deduct(
        user.id, credits_needed, "generation", description=f"Lookbook: {credits_needed} items"
    )

    job = GenerationJob(
        user_id=user.id,
        job_type="lookbook",
        status="queued",
        input_params={
            "garment_ids": body.garment_ids,
            "style": body.style,
            "model_type": body.model_type,
            "background": body.background,
        },
        credits_used=credits_needed,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    from app.worker.celery_app import celery_app

    celery_app.send_task(
        "app.worker.tasks.generate_lookbook.generate_lookbook",
        args=[job.id],
        queue="low",
    )

    return JobCreateResponse(job_id=job.id)
