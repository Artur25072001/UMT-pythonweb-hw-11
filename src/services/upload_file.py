"""
Cloudinary file upload service.

This module provides functionality for uploading user avatar images
to Cloudinary and generating optimized image URLs.

:author: Artur
:version: 1.0.0
"""

import cloudinary
import cloudinary.uploader


class UploadFileService:
    """
    Service for uploading files to Cloudinary.

    Handles image upload configuration and generates resized,
    cropped image URLs for user avatars.

    :param cloud_name: Cloudinary cloud name
    :type cloud_name: str
    :param api_key: Cloudinary API key
    :type api_key: int
    :param api_secret: Cloudinary API secret
    :type api_secret: str
    """

    def __init__(self, cloud_name, api_key, api_secret):
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username) -> str:
        """
        Upload an image file to Cloudinary and return the image URL.

        The image is uploaded with a public ID based on the username and
        resized to 250x250 pixels with fill cropping.

        :param file: The uploaded file object
        :type file: UploadFile
        :param username: Username used to create the public ID
        :type username: str
        :return: URL of the processed image on Cloudinary
        :rtype: str
        """
        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url
