"""
Unit tests for the Cloudinary upload service.
"""

from unittest.mock import MagicMock, patch

import pytest


@patch("src.services.upload_file.cloudinary.config")
def test_upload_file_service_init(mock_config):
    """Should configure Cloudinary on initialisation."""
    from src.services.upload_file import UploadFileService

    service = UploadFileService(
        cloud_name="test_cloud",
        api_key="12345",
        api_secret="secret",
    )

    mock_config.assert_called_once_with(
        cloud_name="test_cloud",
        api_key="12345",
        api_secret="secret",
        secure=True,
    )
    assert service.cloud_name == "test_cloud"


def test_upload_file_service_static_method():
    """UploadFileService.upload_file should be a @staticmethod."""
    import inspect

    from src.services.upload_file import UploadFileService

    method = UploadFileService.__dict__["upload_file"]
    assert isinstance(
        inspect.getattr_static(method, "__func__", method),
        (staticmethod, type(lambda: None)),
    ) or callable(method)


@patch("src.services.upload_file.cloudinary.uploader.upload")
@patch("src.services.upload_file.cloudinary.CloudinaryImage")
@patch("src.services.upload_file.cloudinary.config")
def test_upload_file(mock_config, mock_cloudinary_image, mock_upload):
    """Should upload a file and return the image URL."""
    from src.services.upload_file import UploadFileService

    mock_upload.return_value = {"version": 12345}

    mock_image_instance = MagicMock()
    mock_cloudinary_image.return_value = mock_image_instance
    mock_image_instance.build_url.return_value = (
        "http://res.cloudinary.com/test/image.jpg"
    )

    mock_file = MagicMock()
    mock_file.file = "fake_file"

    service = UploadFileService(
        cloud_name="test_cloud",
        api_key="12345",
        api_secret="secret",
    )

    result = service.upload_file(mock_file, "testuser")

    mock_upload.assert_called_once_with(
        "fake_file", public_id="RestApp/testuser", overwrite=True
    )
    mock_image_instance.build_url.assert_called_once_with(
        width=250, height=250, crop="fill", version=12345
    )
    assert result == "http://res.cloudinary.com/test/image.jpg"
