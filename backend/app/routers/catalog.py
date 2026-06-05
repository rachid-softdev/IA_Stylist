import csv
import io
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from pydantic import BaseModel

from app.dependencies import verify_brand_membership, verify_brand_admin_access
from app.db.session import get_db
from app.models.garment import Garment
from app.models.brand import Brand
from app.schemas.common import GarmentResponse, GarmentCreateRequest, GarmentUpdateRequest
from app.services.image_validation import validate_garment_image

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/{brand_id}/garments")
async def list_garments(
    brand_id: str = Depends(verify_brand_membership),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category: Optional[str] = None,
    status_filter: Optional[str] = Query(default="active", alias="status"),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List garments in a brand's catalog."""
    query = select(Garment).where(Garment.brand_id == brand_id)

    if status_filter:
        query = query.where(Garment.status == status_filter)
    if category:
        query = query.where(Garment.category == category)
    if search:
        query = query.where(
            Garment.name.ilike(f"%{search}%") | Garment.sku.ilike(f"%{search}%")
        )

    count_query = select(func.count(Garment.id)).where(Garment.brand_id == brand_id)
    if status_filter:
        count_query = count_query.where(Garment.status == status_filter)
    if category:
        count_query = count_query.where(Garment.category == category)
    if search:
        count_query = count_query.where(
            Garment.name.ilike(f"%{search}%") | Garment.sku.ilike(f"%{search}%")
        )
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    query = query.order_by(desc(Garment.created_at))
    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    garments = result.scalars().all()

    return {
        "data": garments,
        "meta": {"page": page, "page_size": page_size, "total": total, "total_pages": max(1, -(-total // page_size))},
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
        garment_metadata=body.metadata,
        status="validating",
    )
    db.add(garment)
    await db.commit()
    await db.refresh(garment)

    # Run image validation in background
    try:
        validation = await validate_garment_image(garment.image_url)
        garment.status = "active" if validation["valid"] else "failed"
        if validation["reasons"]:
            garment.garment_metadata = {
                **(garment.garment_metadata or {}),
                "validation": validation,
            }
        await db.commit()
        await db.refresh(garment)
    except Exception as e:
        logger.warning("Validation failed for garment %s: %s", garment.id, str(e))

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


class BatchDeleteRequest(BaseModel):
    ids: list[str]


@router.post("/{brand_id}/garments/batch-delete")
async def batch_delete_garments(
    body: BatchDeleteRequest,
    brand_id: str = Depends(verify_brand_admin_access),
    db: AsyncSession = Depends(get_db),
):
    """Batch delete garments."""
    if not body.ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No IDs provided")

    result = await db.execute(
        select(Garment).where(
            Garment.brand_id == brand_id,
            Garment.id.in_(body.ids),
        )
    )
    garments = result.scalars().all()

    for g in garments:
        await db.delete(g)
    await db.commit()

    return {"deleted": len(garments)}


@router.post("/{brand_id}/import")
async def import_csv(
    brand_id: str = Depends(verify_brand_admin_access),
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
):
    """Import garments from CSV file."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported",
        )

    content = await file.read()
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    required_fields = {"sku", "name", "category"}
    if not reader.fieldnames or not required_fields.issubset(reader.fieldnames):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CSV must contain columns: {', '.join(required_fields)}",
        )

    imported = 0
    errors = []

    for row_num, row in enumerate(reader, start=2):
        try:
            if not row.get("sku") or not row.get("name") or not row.get("category"):
                errors.append({"row": row_num, "error": "Missing required fields"})
                continue

            garment = Garment(
                brand_id=brand_id,
                sku=row["sku"].strip(),
                name=row["name"].strip(),
                category=row["category"].strip(),
                image_url=row.get("image_url", "").strip() or "",
                garment_metadata={
                    k: v.strip() for k, v in row.items()
                    if k not in ("sku", "name", "category", "image_url") and v
                } or None,
                status="validating",
            )
            db.add(garment)
            imported += 1
        except Exception as e:
            errors.append({"row": row_num, "error": str(e)})

    await db.commit()

    return {
        "imported": imported,
        "errors": errors,
        "total_rows": len(list(csv.DictReader(io.StringIO(text)))),
    }
