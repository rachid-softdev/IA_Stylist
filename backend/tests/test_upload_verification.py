"""Tests for upload verification — magic byte detection and R2 error handling (M-03 + M-07 combined).

Verifies:
- Invalid files are rejected with 400 and deleted from R2
- Valid files are accepted with correct detected_type
- Size mismatch between client and R2 is logged but still accepted
- R2 404 errors return 404
"""
import json
import logging
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

import botocore.exceptions

from app.routers.upload import _detect_image_type, IMAGE_MAGIC_BYTES


# ─── Pure function tests for _detect_image_type ────────────────────────


class TestDetectImageType:
    """Test the pure _detect_image_type helper function."""

    def test_jpeg_magic_bytes(self):
        """JPEG signature FF D8 FF must be detected as image/jpeg."""
        assert _detect_image_type(b"\xff\xd8\xff") == "image/jpeg"
        assert _detect_image_type(b"\xff\xd8\xff\xe0") == "image/jpeg"
        assert _detect_image_type(b"\xff\xd8\xff\xdb") == "image/jpeg"

    def test_png_magic_bytes(self):
        """PNG signature must be detected as image/png."""
        assert _detect_image_type(b"\x89PNG\r\n\x1a\n") == "image/png"
        assert _detect_image_type(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR") == "image/png"

    def test_webp_magic_bytes(self):
        """WebP signature (RIFF prefix) must be detected as image/webp."""
        assert _detect_image_type(b"RIFF") == "image/webp"
        assert _detect_image_type(b"RIFF\x00\x00\x00\x00WEBP") == "image/webp"

    def test_invalid_bytes_return_none(self):
        """Non-image bytes must return None."""
        assert _detect_image_type(b"\x00\x00\x00\x00") is None
        assert _detect_image_type(b"") is None
        assert _detect_image_type(b"GIF89a") is None
        assert _detect_image_type(b"<!DOCTYPE html>") is None

    def test_short_bytes_returns_none(self):
        """Bytes shorter than any magic signature must return None."""
        assert _detect_image_type(b"\xff\xd8") is None  # JPEG needs 3 bytes
        assert _detect_image_type(b"\x89PN") is None  # Incomplete PNG


# ─── Full-stack tests via HTTP + mocked R2 ────────────────────────────


# Shared mock user for auth override
from app.models.user import User

_MOCK_USER = User(
    id="test-user-upload",
    email="upload-test@vfs.ai",
    plan="free",
    credits=10,
)


def _make_r2_mock(body_bytes: bytes, content_length: int = 50000):
    """Create a mock R2 client returning given body bytes."""
    client = MagicMock()
    client.get_object.return_value = {
        "ContentLength": content_length,
        "Body": MagicMock(read=MagicMock(return_value=body_bytes)),
    }
    return client


def _make_r2_404_error():
    """Create a botocore ClientError for 404/NoSuchKey."""
    return botocore.exceptions.ClientError(
        error_response={"Error": {"Code": "NoSuchKey", "Message": "Not found"}},
        operation_name="GetObject",
    )


# PNG header (8 magic bytes) + 8 bytes of IHDR chunk data = 16 bytes total
# Matches what R2 returns for a Range: bytes=0-15 request
_PNG_HEADER = b"\x89PNG\r\n\x1a\n\x00\x00\x00\x00\x00\x00\x00\x00"


@pytest.mark.asyncio
async def test_invalid_magic_bytes_rejected(client):
    """R2 returning non-image bytes must return 400 and delete_object called."""
    from app.main import app
    from app.dependencies import get_current_user

    # Override auth
    app.dependency_overrides[get_current_user] = lambda: _MOCK_USER

    try:
        # Get CSRF tokens
        token_resp = await client.get("/v1/auth/csrf-token")
        csrf_cookie = token_resp.cookies["csrf_token"]
        raw_token = token_resp.json()["token"]
        assert csrf_cookie, "CSRF cookie must be set"

        with patch("app.routers.upload._get_client") as mock_get_client:
            mock_client = _make_r2_mock(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
            mock_get_client.return_value = mock_client

            response = await client.post(
                "/v1/upload/confirm",
                json={"r2_key": "test/invalid-file.bin", "size": 12345},
                cookies={"csrf_token": csrf_cookie},
                headers={"X-CSRF-Token": raw_token},
            )

        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        # FastAPI HTTPException serializes detail dict directly
        detail = data.get("detail", data)
        assert detail["code"] == "INVALID_FILE_TYPE"
        assert "file does not match" in detail["message"].lower()
        mock_client.delete_object.assert_called_once()
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_valid_png_accepted(client):
    """R2 returning PNG magic bytes must return 200 with detected_type='image/png'."""
    from app.main import app
    from app.dependencies import get_current_user

    app.dependency_overrides[get_current_user] = lambda: _MOCK_USER

    try:
        # Get CSRF tokens
        token_resp = await client.get("/v1/auth/csrf-token")
        csrf_cookie = token_resp.cookies["csrf_token"]
        raw_token = token_resp.json()["token"]

        with patch("app.routers.upload._get_client") as mock_get_client:
            mock_client = _make_r2_mock(_PNG_HEADER, content_length=50000)
            mock_get_client.return_value = mock_client

            response = await client.post(
                "/v1/upload/confirm",
                json={"r2_key": "test/valid-image.png", "size": 50000},
                cookies={"csrf_token": csrf_cookie},
                headers={"X-CSRF-Token": raw_token},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["detected_type"] == "image/png"
        assert data["size"] == 50000
        assert data["status"] == "confirmed"
        # delete_object must NOT be called for valid files
        mock_client.delete_object.assert_not_called()
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_size_mismatch_logged(caplog, client):
    """Client sends size X, R2 returns Y → warning logged but still accepted."""
    from app.main import app
    from app.dependencies import get_current_user

    app.dependency_overrides[get_current_user] = lambda: _MOCK_USER

    try:
        token_resp = await client.get("/v1/auth/csrf-token")
        csrf_cookie = token_resp.cookies["csrf_token"]
        raw_token = token_resp.json()["token"]

        with patch("app.routers.upload._get_client") as mock_get_client:
            # R2 returns 50000 bytes, but client said 12345
            mock_client = _make_r2_mock(_PNG_HEADER, content_length=50000)
            mock_get_client.return_value = mock_client

            with caplog.at_level(logging.WARNING, logger="app.routers.upload"):
                response = await client.post(
                    "/v1/upload/confirm",
                    json={"r2_key": "test/mismatch.png", "size": 12345},
                    cookies={"csrf_token": csrf_cookie},
                    headers={"X-CSRF-Token": raw_token},
                )

        assert response.status_code == 200
        # Verify warning was logged about size mismatch
        assert any("Size mismatch" in record.message for record in caplog.records)
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_r2_404_returns_404(client):
    """R2 raises ClientError with 404 → endpoint returns 404."""
    from app.main import app
    from app.dependencies import get_current_user

    app.dependency_overrides[get_current_user] = lambda: _MOCK_USER

    try:
        token_resp = await client.get("/v1/auth/csrf-token")
        csrf_cookie = token_resp.cookies["csrf_token"]
        raw_token = token_resp.json()["token"]

        with patch("app.routers.upload._get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_object.side_effect = _make_r2_404_error()
            mock_get_client.return_value = mock_client

            response = await client.post(
                "/v1/upload/confirm",
                json={"r2_key": "test/nonexistent.png", "size": 100},
                cookies={"csrf_token": csrf_cookie},
                headers={"X-CSRF-Token": raw_token},
            )

        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        data = response.json()
        detail = data.get("detail", data)
        assert detail["code"] == "FILE_NOT_FOUND"
    finally:
        app.dependency_overrides.pop(get_current_user, None)
