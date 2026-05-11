from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import Optional

from app.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.job import GenerationJob
from app.models.collection import Collection, CollectionItem
from app.services.security import generate_share_token
from app.schemas.common import (
    CollectionResponse,
    CollectionCreateRequest,
    CollectionUpdateRequest,
    JobResponse,
)

router = APIRouter()


# ─── Jobs / Gallery ───────────────────────────────────────

@router.get("/")
async def list_dressing(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category: Optional[str] = None,
    status: Optional[str] = Query(default="done"),
    favorite: Optional[bool] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's generated try-ons (dressing gallery)."""
    query = select(GenerationJob).where(
        GenerationJob.user_id == user.id,
        GenerationJob.job_type == "image",
    )

    if status:
        query = query.where(GenerationJob.status == status)
    if category:
        query = query.where(GenerationJob.input_params["category"].as_string() == category)

    query = query.order_by(desc(GenerationJob.created_at))

    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    jobs = result.scalars().all()

    return {
        "data": jobs,
        "meta": {"page": page, "page_size": page_size},
    }


@router.get("/history")
async def list_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all user's generation jobs (chronological)."""
    query = (
        select(GenerationJob)
        .where(GenerationJob.user_id == user.id)
        .order_by(desc(GenerationJob.created_at))
    )
    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    jobs = result.scalars().all()

    return {
        "data": jobs,
        "meta": {"page": page, "page_size": page_size},
    }


@router.delete("/{job_id}")
async def delete_result(
    job_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a generation result."""
    result = await db.execute(
        select(GenerationJob).where(
            GenerationJob.id == job_id,
            GenerationJob.user_id == user.id,
        )
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": "Job not found"})

    await db.delete(job)
    await db.commit()

    return {"message": "Deleted"}


# ─── Collections ──────────────────────────────────────────

@router.get("/collections")
async def list_collections(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's collections."""
    result = await db.execute(
        select(Collection)
        .where(Collection.user_id == user.id)
        .order_by(desc(Collection.created_at))
    )
    collections = result.scalars().all()

    return {"data": collections}


@router.post("/collections", response_model=CollectionResponse)
async def create_collection(
    body: CollectionCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new collection."""
    collection = Collection(
        user_id=user.id,
        name=body.name,
        is_public=body.is_public,
    )
    if body.is_public:
        collection.share_token = generate_share_token()

    db.add(collection)
    await db.commit()
    await db.refresh(collection)

    return collection


@router.put("/collections/{collection_id}")
async def update_collection(
    collection_id: str,
    body: CollectionUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a collection."""
    result = await db.execute(
        select(Collection).where(
            Collection.id == collection_id,
            Collection.user_id == user.id,
        )
    )
    collection = result.scalar_one_or_none()

    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if body.name is not None:
        collection.name = body.name
    if body.is_public is not None:
        collection.is_public = body.is_public
        if body.is_public and not collection.share_token:
            collection.share_token = generate_share_token()

    await db.commit()
    await db.refresh(collection)

    return collection


@router.delete("/collections/{collection_id}")
async def delete_collection(
    collection_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a collection (items cascade)."""
    result = await db.execute(
        select(Collection).where(
            Collection.id == collection_id,
            Collection.user_id == user.id,
        )
    )
    collection = result.scalar_one_or_none()

    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    await db.delete(collection)
    await db.commit()

    return {"message": "Deleted"}


@router.post("/collections/{collection_id}/items")
async def add_to_collection(
    collection_id: str,
    job_id: str = Query(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a job to a collection."""
    # Verify ownership
    result = await db.execute(
        select(Collection).where(
            Collection.id == collection_id,
            Collection.user_id == user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    item = CollectionItem(collection_id=collection_id, job_id=job_id)
    db.add(item)
    await db.commit()

    return {"message": "Added"}


@router.delete("/collections/{collection_id}/items/{job_id}")
async def remove_from_collection(
    collection_id: str,
    job_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a job from a collection."""
    result = await db.execute(
        select(CollectionItem).where(
            CollectionItem.collection_id == collection_id,
            CollectionItem.job_id == job_id,
        )
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    await db.delete(item)
    await db.commit()

    return {"message": "Removed"}
