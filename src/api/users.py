"""
User profile API routes.

This module provides endpoints for managing user profiles,
including retrieving current user info and updating avatars.

:author: Artur
:version: 1.0.0
"""

from fastapi import APIRouter, Depends, Request
from src.schemas import User
from src.services.auth import get_current_user, RoleChecker
from src.services.users import UserService
from src.database.db import get_db
from src.database.redis import get_redis
from src.services.cache import delete_cached_user
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.upload_file import UploadFileService
from fastapi import File, UploadFile
from src.conf.config import settings
from src.conf.limiter import limiter
import redis.asyncio as aioredis

require_admin = RoleChecker(["admin"])

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/me", response_model=User, description="No more than 10 requests per minute"
)
@limiter.limit("10/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
    Retrieve the current authenticated user's profile.

    Rate limited to 10 requests per minute.

    :param request: The incoming request object (used by limiter)
    :type request: Request
    :param user: Currently authenticated user
    :type user: User
    :return: The authenticated user's profile
    :rtype: User
    """
    return user


@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
    _: bool = Depends(require_admin),
):
    """
    Update the current user's avatar image.

    Uploads the provided image file to Cloudinary and updates the user's
    avatar URL in the database. Invalidates the Redis cache so the
    updated avatar is returned on subsequent requests.

    **Admin-only endpoint.** Only users with the "admin" role can
    change their avatar.

    :param file: The uploaded image file
    :type file: UploadFile
    :param user: Currently authenticated user
    :type user: User
    :param db: Database session dependency
    :type db: AsyncSession
    :param redis: Redis client dependency
    :type redis: aioredis.Redis
    :param _: Admin role check
    :type _: bool
    :return: The updated user profile with new avatar URL
    :rtype: User
    """
    avatar_url = UploadFileService(
        settings.CLOUDINARY_NAME,
        settings.CLOUDINARY_API_KEY,
        settings.CLOUDINARY_API_SECRET,
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    # Invalidate cache so the next request fetches the updated user
    if redis:
        await delete_cached_user(redis, user.username)

    return user
