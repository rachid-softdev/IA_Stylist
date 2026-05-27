import uuid
import boto3
import botocore.exceptions
from botocore.config import Config
from app.config import get_settings

settings = get_settings()

_s3_client = None


def _get_client():
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client(
            "s3",
            endpoint_url=settings.r2_endpoint_url,
            aws_access_key_id=settings.R2_ACCESS_KEY,
            aws_secret_access_key=settings.R2_SECRET_KEY,
            config=Config(signature_version="s3v4", region_name="auto"),
        )
    return _s3_client


def generate_presigned_upload_url(
    user_id: str,
    folder: str,
    filename: str,
    content_type: str,
    expires: int = 300,
) -> tuple[str, str, str]:
    """
    Generate a presigned URL for client-side upload.

    Returns (upload_url, r2_key, public_url).
    """
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "png"
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    r2_key = f"{folder}/{user_id}/{unique_name}"

    client = _get_client()
    upload_url = client.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": settings.R2_BUCKET,
            "Key": r2_key,
            "ContentType": content_type,
        },
        ExpiresIn=expires,
    )

    public_url = f"{settings.R2_PUBLIC_URL}/{r2_key}"
    return upload_url, r2_key, public_url


def generate_presigned_download_url(r2_key: str, expires: int = 900) -> str:
    """Generate a presigned URL for temporary file access."""
    client = _get_client()
    return client.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": settings.R2_BUCKET, "Key": r2_key},
        ExpiresIn=expires,
    )


def delete_file(r2_key: str) -> None:
    """Delete a file from R2."""
    client = _get_client()
    client.delete_object(Bucket=settings.R2_BUCKET, Key=r2_key)


def get_public_url(r2_key: str) -> str:
    """Get the public URL for a stored file."""
    if settings.R2_PUBLIC_URL:
        return f"{settings.R2_PUBLIC_URL}/{r2_key}"
    return r2_key


def ensure_bucket_exists():
    """Ensure the R2 bucket exists, create if needed."""
    client = _get_client()
    try:
        client.head_bucket(Bucket=settings.R2_BUCKET)
    except botocore.exceptions.ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code == "404" or error_code == "NoSuchBucket":
            client.create_bucket(Bucket=settings.R2_BUCKET)
        else:
            raise  # Real error (auth, network, etc.)
