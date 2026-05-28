import logging
from fastapi import APIRouter, Depends, HTTPException, status
from app.config import get_settings
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import PresignedUrlRequest, PresignedUrlResponse, UploadConfirmRequest
from app.services.storage import generate_presigned_upload_url, get_public_url, _get_client
import botocore.exceptions

logger = logging.getLogger(__name__)

# Magic byte signatures for allowed image formats
IMAGE_MAGIC_BYTES = [
    (b"\xff\xd8\xff", "image/jpeg"),       # JPEG
    (b"\x89PNG\r\n\x1a\n", "image/png"),   # PNG
    (b"RIFF", "image/webp"),                # WebP (starts with RIFF....WEBP)
]


def _detect_image_type(header_bytes: bytes) -> str | None:
    """Detect image MIME type from first bytes."""
    for magic, mime in IMAGE_MAGIC_BYTES:
        if header_bytes.startswith(magic):
            return mime
    return None

settings = get_settings()
router = APIRouter()


@router.post("/presigned-url", response_model=PresignedUrlResponse)
async def get_presigned_url(
    body: PresignedUrlRequest,
    user: User = Depends(get_current_user),
):
    """Generate a presigned URL for client-side file upload."""
    if body.size is not None and body.size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "code": "FILE_TOO_LARGE",
                "message": f"File size exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit",
            },
        )
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
    client = _get_client()
    try:
        # Single R2 GET with Range for both size + magic bytes (M-03 + M-07 combined)
        obj_response = client.get_object(
            Bucket=settings.R2_BUCKET,
            Key=body.r2_key,
            Range="bytes=0-15",
        )
        actual_size = int(obj_response["ContentLength"])
        header_bytes = obj_response["Body"].read(16)

        # M-03: Verify file exists and size matches
        if actual_size != body.size:
            logger.warning(
                "Size mismatch: client=%s actual=%s r2_key=%s user=%s",
                body.size, actual_size, body.r2_key, user.id,
            )

        # M-07: Verify magic bytes match an allowed image type
        detected_type = _detect_image_type(header_bytes)
        if detected_type is None:
            client.delete_object(Bucket=settings.R2_BUCKET, Key=body.r2_key)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_FILE_TYPE",
                    "message": "Uploaded file does not match allowed image formats",
                },
            )

    except HTTPException:
        raise
    except botocore.exceptions.ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code in ("404", "NoSuchKey", "NoSuchBucket"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "FILE_NOT_FOUND", "message": "Uploaded file not found in storage"},
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "STORAGE_ERROR", "message": "Failed to verify uploaded file"},
        )

    public_url = get_public_url(body.r2_key)
    return {
        "r2_key": body.r2_key,
        "public_url": public_url,
        "size": actual_size,
        "detected_type": detected_type,
        "status": "confirmed",
    }
