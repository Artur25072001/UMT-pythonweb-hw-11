"""
Authentication API routes.

This module provides endpoints for user registration, login,
email confirmation, and token management.

:author: Artur
:version: 1.0.0
"""

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Security,
    BackgroundTasks,
    Request,
)

from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from src.conf.config import settings
from src.schemas import (
    UserCreate,
    Token,
    User,
    RequestEmail,
    RequestPasswordReset,
    ResetPassword,
)

from src.services.auth import create_access_token, Hash, get_email_from_token
from src.services.users import UserService
from src.services.email import send_email, send_password_reset_email
from src.database.db import get_db
from src.database.redis import get_redis
from src.services.cache import set_cached_user, delete_cached_user
import redis.asyncio as aioredis

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Register a new user.

    Creates a new user account with the provided data. Sends a confirmation
    email to the user's email address in the background.

    :param user_data: User registration data
    :type user_data: UserCreate
    :param background_tasks: Background tasks manager for sending emails
    :type background_tasks: BackgroundTasks
    :param request: The incoming request object
    :type request: Request
    :param db: Database session dependency
    :type db: Session
    :return: The newly created user
    :rtype: User
    :raises HTTPException 409: If the email or username already exists
    """
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким email вже існує",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким іменем вже існує",
        )
    user_data.password = Hash().get_password_hash(user_data.password)
    role = "admin" if user_data.email == settings.ADMIN_EMAIL else "user"
    new_user = await user_service.create_user(user_data, role=role)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return new_user


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Request a new email confirmation link.

    Sends a confirmation email to the specified address if the user exists
    and has not yet confirmed their email.

    :param body: Email request data
    :type body: RequestEmail
    :param background_tasks: Background tasks manager for sending emails
    :type background_tasks: BackgroundTasks
    :param request: The incoming request object
    :type request: Request
    :param db: Database session dependency
    :type db: Session
    :return: Confirmation message
    :rtype: dict
    :raises HTTPException 404: If no user with the given email exists
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Користувача з таким email не знайдено",
        )

    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}

    background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Перевірте свою електронну пошту для підтвердження"}


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    """
    Authenticate a user and return an access token.

    Validates the user's credentials and returns a JWT access token
    upon successful authentication. The authenticated user is cached
    in Redis for subsequent requests.

    :param form_data: OAuth2 password form data
    :type form_data: OAuth2PasswordRequestForm
    :param db: Database session dependency
    :type db: Session
    :param redis: Redis client dependency
    :type redis: aioredis.Redis
    :return: Access token and token type
    :rtype: Token
    :raises HTTPException 401: If credentials are invalid or email is not confirmed
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильний логін або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Електронна адреса не підтверджена",
        )
    # Cache the user in Redis after successful login
    if redis:
        await set_cached_user(redis, user)
    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(
    token: str,
    db: Session = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    """
    Confirm a user's email address using a verification token.

    Decodes the token to extract the email and marks the user as confirmed.
    Invalidates the Redis cache for the user so the updated data is fetched
    on the next request.

    :param token: Email verification token
    :type token: str
    :param db: Database session dependency
    :type db: Session
    :param redis: Redis client dependency
    :type redis: aioredis.Redis
    :return: Confirmation message
    :rtype: dict
    :raises HTTPException 400: If verification token is invalid
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    await user_service.confirmed_email(email)
    # Invalidate cache so the confirmed status is updated
    if redis:
        await delete_cached_user(redis, user.username)
    return {"message": "Електронну пошту підтверджено"}


@router.post("/forgot-password")
async def forgot_password(
    body: RequestPasswordReset,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Request a password reset email.

    If a user with the given email exists, sends a password reset link
    to that email. Always returns a success message to prevent email
    enumeration.

    :param body: Password reset request data
    :type body: RequestPasswordReset
    :param background_tasks: Background tasks manager for sending emails
    :type background_tasks: BackgroundTasks
    :param request: The incoming request object
    :type request: Request
    :param db: Database session dependency
    :type db: Session
    :return: Confirmation message
    :rtype: dict
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    # Always return success regardless of whether the user exists
    # to prevent email enumeration attacks
    if user:
        background_tasks.add_task(
            send_password_reset_email, user.email, user.username, request.base_url
        )

    return {
        "message": "Якщо обліковий запис існує, лист для скидання пароля надіслано на вашу електронну пошту"
    }


@router.post("/reset-password/{token}")
async def reset_password(
    token: str,
    body: ResetPassword,
    db: Session = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    """
    Reset a user's password using a valid reset token.

    Decodes the token to extract the email, hashes the new password,
    and updates the user record. Invalidates the Redis cache for the user.

    :param token: JWT password reset token (from URL path)
    :type token: str
    :param body: Reset password data with the new password
    :type body: ResetPassword
    :param db: Database session dependency
    :type db: Session
    :param redis: Redis client dependency
    :type redis: aioredis.Redis
    :return: Success message
    :rtype: dict
    :raises HTTPException 400: If the token or user is invalid
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неправильний токен для скидання пароля",
        )

    hashed_password = Hash().get_password_hash(body.new_password)
    await user_service.update_password(email, hashed_password)

    # Invalidate Redis cache so stale data is not served
    if redis:
        await delete_cached_user(redis, user.username)

    return {"message": "Пароль успішно змінено"}
