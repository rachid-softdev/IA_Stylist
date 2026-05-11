from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import PresignedUrlRequest, PresignedUrlResponse, UploadConfirmRequest
from app.services.storage import generate_presigned_upload_url, get_public_url

router = APIRouter()


@router.post("/presigned-url", response_model=PresignedUrlResponse)
async def get_presigned_url(
    body: PresignedUrlRequest,
    user: User = Depends(get_current_user),
):
    """Generate a presigned URL for client-side file upload."""
    upload_url, r2_key, public_url = generate_presigned_upload_url(
        user_id=user.id,
        folder=body.folder,
        filename=body.filename,
        content_type=body.content_type,
        expires=300,
    )

    return PresignedUrlResponse(
        upload_url=upload_url,
        r2_key=r2_key,
        public_url=public_url,
    )


@router.post("/confirm")
async def confirm_upload(
    body: UploadConfirmRequest,
    user: User = Depends(get_current_user),
):
    """Confirm a completed upload and trigger post-processing if needed."""
    public_url = get_public_url(body.r2_key)

    # If it's a user profile photo, we could trigger analysis here
    # if body.folder starts with "uploads/raw" ...

    return {
        "r2_key": body.r2_key,
        "public_url": public_url,
        "size": body.size,
        "status": "confirmed",
    }
