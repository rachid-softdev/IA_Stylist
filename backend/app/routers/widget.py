import json
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status, Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from app.db.session import get_db
from app.models.api_key import ApiKey
from app.models.brand import Brand
from app.models.garment import Garment
from app.models.job import GenerationJob
from app.services.security import hash_api_key, verify_api_key
from app.services.websocket import push_job_update

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/auth")
async def widget_auth(
    api_key: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Authenticate a widget session and return a short-lived token."""
    result = await db.execute(
        select(ApiKey).where(
            ApiKey.is_active == True,
            ApiKey.expires_at.is_(None) | (ApiKey.expires_at > "now()"),
        )
    )
    keys = result.scalars().all()

    matched_key = None
    for key in keys:
        if verify_api_key(api_key, key.key_hash):
            matched_key = key
            break

    if not matched_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_API_KEY", "message": "Invalid or expired API key"},
        )

    return {
        "data": {
            "authenticated": True,
            "brand_id": matched_key.brand_id,
        }
    }


@router.post("/generate")
async def widget_generate(
    file: UploadFile = File(...),
    api_key: str = Form(...),
    product_id: str = Form(...),
    sku: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Generate a try-on from the widget."""
    # Verify API key
    result = await db.execute(
        select(ApiKey).where(ApiKey.is_active == True)
    )
    keys = result.scalars().all()
    matched_key = None
    for key in keys:
        if verify_api_key(api_key, key.key_hash):
            matched_key = key
            break

    if not matched_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    brand_id = matched_key.brand_id

    # Find garment by SKU
    result = await db.execute(
        select(Garment).where(
            Garment.brand_id == brand_id,
            Garment.sku == sku,
            Garment.status == "active",
        )
    )
    garment = result.scalar_one_or_none()

    if not garment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "GARMENT_NOT_FOUND", "message": "Garment not found for this SKU"},
        )

    # Upload file to R2
    from app.services.storage import upload_file_to_r2
    import uuid

    r2_key = f"widget/{brand_id}/{uuid.uuid4().hex}_{file.filename}"
    file_content = await file.read()
    image_url = upload_file_to_r2(r2_key, file_content, file.content_type or "image/jpeg")

    # Create job
    job = GenerationJob(
        user_id=f"widget_{brand_id}",
        brand_id=brand_id,
        job_type="image",
        status="queued",
        garment_id=garment.id,
        input_params={
            "model_photo": image_url,
            "garment_image": garment.image_url,
            "category": garment.category,
        },
        credits_used=1,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Enqueue task
    from app.worker.celery_app import celery_app

    celery_app.send_task(
        "app.worker.tasks.generate_image.generate_tryon_image",
        args=[job.id],
        queue="default",
    )

    return {
        "data": {
            "job_id": job.id,
            "status": "queued",
        }
    }


@router.post("/track")
async def widget_track(request: Request):
    """Track widget events."""
    try:
        body = await request.json()
        logger.info("Widget event: %s", json.dumps(body))
    except Exception:
        pass
    return {"status": "ok"}
