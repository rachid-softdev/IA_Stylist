from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User, UserProfile
from app.schemas.common import StylistRecommendation, StylistOutfit, StylistFeedbackRequest

router = APIRouter()


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

    # In production: call AI vision model here
    # For now, return placeholder
    analysis = {
        "morphologie": "athletic",
        "teint": "medium",
        "style": "casual",
        "detected_at": "auto",
    }

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
    # In production: call LLM with user profile + garment data
    # For now, return placeholder
    return {
        "data": {
            "garment_id": garment_id,
            "fit_advice": "Ce vêtement en coupe regular devrait bien correspondre à votre morphologie.",
            "style_advice": "Associez-le avec un jean brut pour un look casual chic.",
            "color_advice": "La teinte sable s'accorde bien avec votre teint.",
            "fit_score": 8,
        }
    }


@router.get("/outfits")
async def get_suggested_outfits(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get AI-suggested complete outfits."""
    # In production: LLM-powered outfit matching
    return {
        "data": [
            {
                "items": [],
                "description": "Completez votre profil pour des suggestions personnalisées.",
                "occasion": "daily",
            }
        ]
    }


@router.post("/feedback")
async def submit_feedback(
    body: StylistFeedbackRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit feedback on AI stylist recommendations."""
    # In production: store feedback for model improvement
    return {"status": "ok", "message": "Feedback recorded, merci !"}
