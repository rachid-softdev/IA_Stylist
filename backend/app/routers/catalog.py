from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional

from app.dependencies import verify_brand_membership, verify_brand_admin_access
from app.db.session import get_db
from app.models.garment import Garment
from app.schemas.common import GarmentResponse, GarmentCreateRequest, GarmentUpdateRequest

router = APIRouter()


@router.get("/{brand_id}/garments")
async def list_garments(
    brand_id: str = Depends(verify_brand_membership),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category: Optional[str] = None,
    status_filter: Optional[str] = Query(default="active", alias="status"),
    db: AsyncSession = Depends(get_db),
):
    """List garments in a brand's catalog."""
    query = select(Garment).where(Garment.brand_id == brand_id)

    if status_filter:
        query = query.where(Garment.status == status_filter)
    if category:
        query = query.where(Garment.category == category)

    query = query.order_by(desc(Garment.created_at))
    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    garments = result.scalars().all()

    return {
        "data": garments,
        "meta": {"page": page, "page_size": page_size},
    }


@router.post("/{brand_id}/garments", response_model=GarmentResponse)
async def create_garment(
    body: GarmentCreateRequest,
    brand_id: str = Depends(verify_brand_admin_access),
    db: AsyncSession = Depends(get_db),
):
    """Add a garment to the catalog."""
    garment = Garment(
        brand_id=brand_id,
        sku=body.sku,
        name=body.name,
        category=body.category,
        image_url=body.image_url,
        metadata=body.metadata,
        status="validating",
    )
    db.add(garment)
    await db.commit()
    await db.refresh(garment)

    return garment


@router.get("/{brand_id}/garments/{garment_id}", response_model=GarmentResponse)
async def get_garment(
    garment_id: str,
    brand_id: str = Depends(verify_brand_membership),
    db: AsyncSession = Depends(get_db),
):
    """Get a single garment."""
    result = await db.execute(
        select(Garment).where(Garment.id == garment_id, Garment.brand_id == brand_id)
    )
    garment = result.scalar_one_or_none()

    if not garment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return garment


@router.put("/{brand_id}/garments/{garment_id}", response_model=GarmentResponse)
async def update_garment(
    garment_id: str,
    body: GarmentUpdateRequest,
    brand_id: str = Depends(verify_brand_admin_access),
    db: AsyncSession = Depends(get_db),
):
    """Update a garment."""
    result = await db.execute(
        select(Garment).where(Garment.id == garment_id, Garment.brand_id == brand_id)
    )
    garment = result.scalar_one_or_none()

    if not garment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(garment, field, value)

    await db.commit()
    await db.refresh(garment)

    return garment


@router.delete("/{brand_id}/garments/{garment_id}")
async def delete_garment(
    garment_id: str,
    brand_id: str = Depends(verify_brand_admin_access),
    db: AsyncSession = Depends(get_db),
):
    """Delete a garment."""
    result = await db.execute(
        select(Garment).where(Garment.id == garment_id, Garment.brand_id == brand_id)
    )
    garment = result.scalar_one_or_none()

    if not garment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    await db.delete(garment)
    await db.commit()

    return {"message": "Deleted"}
