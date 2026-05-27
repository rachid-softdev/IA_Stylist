import time
import pytest
from unittest.mock import patch, Mock
from app.services.storage import (
    generate_presigned_upload_url,
    generate_presigned_download_url,
    get_public_url,
    delete_file,
)


@pytest.mark.asyncio
async def test_generate_presigned_upload_url():
    with patch('app.services.storage._get_client') as mock_get_client:
        mock_client = Mock()
        mock_client.generate_presigned_url.return_value = "https://upload.url"
        mock_get_client.return_value = mock_client

        upload_url, r2_key, public_url = generate_presigned_upload_url(
            user_id="user-001",
            folder="uploads/raw",
            filename="photo.jpg",
            content_type="image/jpeg",
        )

        assert upload_url == "https://upload.url"
        assert r2_key.startswith("uploads/raw/user-001/")
        assert public_url.endswith(r2_key)


@pytest.mark.parametrize("r2_public_url,expected_pattern", [
    ("", "uploads/raw/user-001/photo.jpg"),
    ("https://cdn.vfs.ai", "cdn.vfs.ai"),
])
def test_get_public_url(r2_public_url: str, expected_pattern: str):
    with patch("app.services.storage.settings.R2_PUBLIC_URL", r2_public_url):
        url = get_public_url("uploads/raw/user-001/photo.jpg")
        assert expected_pattern in url
        assert "uploads/raw/user-001/photo.jpg" in url
