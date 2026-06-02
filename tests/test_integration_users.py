"""
Integration tests for user profile API routes.

Tests the /api/users/me endpoint and admin-only avatar update.
Uses the SQLite test database and TestClient from conftest.
"""

from unittest.mock import Mock, AsyncMock

import pytest

from tests.conftest import test_user, admin_user


def test_get_me(client, get_token):
    """Should return the current authenticated user's profile."""
    response = client.get(
        "api/users/me",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]
    assert "role" in data
    assert data["role"] == "user"


def test_get_me_admin(client, admin_token):
    """Should return the admin user's profile with admin role."""
    response = client.get(
        "api/users/me",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == admin_user["username"]
    assert data["email"] == admin_user["email"]
    assert data["role"] == "admin"


def test_get_me_unauthenticated(client):
    """Should return 401 when no token is provided."""
    response = client.get("api/users/me")
    assert response.status_code == 401, response.text


def test_get_me_invalid_token(client):
    """Should return 401 when an invalid token is provided."""
    response = client.get(
        "api/users/me",
        headers={"Authorization": "Bearer invalid_token_here"},
    )
    assert response.status_code == 401, response.text


def test_update_avatar_admin_success(client, admin_token, monkeypatch):
    """Should allow admin to update avatar successfully."""
    # Mock the Cloudinary upload service
    mock_upload_service = Mock()
    mock_upload_service.upload_file.return_value = "http://new-avatar.url/photo.jpg"
    monkeypatch.setattr(
        "src.api.users.UploadFileService", Mock(return_value=mock_upload_service)
    )

    # Create a mock file
    file_content = b"fake_image_bytes"
    response = client.patch(
        "api/users/avatar",
        files={"file": ("avatar.jpg", file_content, "image/jpeg")},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    # Should succeed for admin
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["avatar"] == "http://new-avatar.url/photo.jpg"


def test_update_avatar_forbidden_for_user(client, get_token, monkeypatch):
    """Should return 403 when a regular user tries to update avatar."""
    mock_upload_service = Mock()
    mock_upload_service.upload_file.return_value = "http://new-avatar.url/photo.jpg"
    monkeypatch.setattr(
        "src.api.users.UploadFileService", Mock(return_value=mock_upload_service)
    )

    file_content = b"fake_image_bytes"
    response = client.patch(
        "api/users/avatar",
        files={"file": ("avatar.jpg", file_content, "image/jpeg")},
        headers={"Authorization": f"Bearer {get_token}"},
    )
    # Should be forbidden for non-admin
    assert response.status_code == 403, response.text
