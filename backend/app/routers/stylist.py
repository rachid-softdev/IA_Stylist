from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User, UserProfile
from app.models.garment import Garment
from app.schemas.common import StylistRecommendation, StylistOutfit, StylistFeedbackRequest
from app.services.ai.stylist import StylistAI

router = APIRouter()
stylist_ai = StylistAI()


@router.get("/profile")
async def get_style_profile(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's AI style profile (morphology, preferences)."""
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = result.scalar_one_or_none()

    if not profile:
        return {
            "status": "no_profile",
            "message": "Upload your photos to create your style profile",
            "data": None,
        }

    return {
        "status": "ok",
        "data": {
            "photos": profile.photos,
            "metadata": profile.metadata,
        },
    }


@router.post("/analyze")
async def analyze_profile(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger AI analysis of user photos for morphology detection."""
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = result.scalar_one_or_none()

    if not profile or not profile.photos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "NO_PHOTOS", "message": "Upload photos first to analyze your profile"},
        )

    photo_url = profile.photos[0]["url"] if isinstance(profile.photos, list) else ""
    analysis = await stylist_ai.analyze_morphology(photo_url, user.id)

    profile.metadata = analysis
    await db.commit()

    return {"status": "ok", "data": analysis}


@router.get("/recommendations/{garment_id}")
async def get_recommendations(
    garment_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get AI stylist recommendations for a specific garment."""
    result = await db.execute(select(Garment).where(Garment.id == garment_id))
    garment = result.scalar_one_or_none()

    if not garment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    profile_result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = profile_result.scalar_one_or_none()
    morphology = (profile.metadata or {}).get("morphologie", "standard") if profile else "standard"

    rec = await stylist_ai.recommend_fit(
        morphology=morphology,
        garment_category=garment.category,
        garment_fit=(garment.garment_metadata or {}).get("fit", "regular"),
        user_id=user.id,
        garment_id=garment_id,
    )

    return {
        "data": {
            "garment_id": garment_id,
            "fit_advice": rec.get("fit_advice", ""),
            "style_advice": rec.get("style_tip", ""),
            "color_advice": rec.get("color_advice", ""),
            "fit_score": rec.get("fit_score", 7),
        }
    }


@router.get("/outfits")
async def get_suggested_outfits(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get AI-suggested complete outfits."""
    profile_result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = profile_result.scalar_one_or_none()
    morphology = (profile.metadata or {}).get("morphologie", "standard") if profile else "standard"

    # Get user's recent garments from dressing
    from app.models.job import GenerationJob

    jobs_result = await db.execute(
        select(GenerationJob).where(
            GenerationJob.user_id == user.id,
            GenerationJob.garment_id.isnot(None),
            GenerationJob.status == "done",
        ).limit(20)
    )
    jobs = jobs_result.scalars().all()

    wardrobe = []
    for job in jobs:
        if job.garment_id:
            g_result = await db.execute(select(Garment).where(Garment.id == job.garment_id))
            g = g_result.scalar_one_or_none()
            if g:
                wardrobe.append({"name": g.name, "category": g.category, "id": g.id})

    outfits = await stylist_ai.suggest_outfits(morphology, wardrobe, user.id)

    return {"data": outfits or []}


@router.post("/feedback")
async def submit_feedback(
    body: StylistFeedbackRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit feedback on AI stylist recommendations."""
    # In production: store feedback for model improvement
    import json

    feedback_data = {
        "user_id": user.id,
        "job_id": body.job_id,
        "helpful": body.helpful,
        "timestamp": "now",
    }
    logger = __import__("logging").getLogger(__name__)
    logger.info("Stylist feedback: %s", json.dumps(feedback_data))

    return {"status": "ok", "message": "Feedback recorded, merci !"}
