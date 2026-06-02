"""
Application configuration settings.

This module defines the Settings class that loads environment variables
for database, JWT, email, and Cloudinary configuration.

:author: Artur
:version: 1.0.0
"""

from pydantic import ConfigDict, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Configuration class that reads from a .env file and provides
    typed access to all application configuration values.

    :ivar DB_URL: Database connection URL
    :ivar JWT_SECRET: Secret key for JWT token encoding/decoding
    :ivar JWT_ALGORITHM: Algorithm used for JWT tokens (default: HS256)
    :ivar JWT_EXPIRATION_SECONDS: Token expiration time in seconds (default: 3600)
    :ivar MAIL_USERNAME: Email account username
    :ivar MAIL_PASSWORD: Email account password
    :ivar MAIL_FROM: Sender email address
    :ivar MAIL_PORT: SMTP server port (default: 587)
    :ivar MAIL_SERVER: SMTP server hostname
    :ivar MAIL_FROM_NAME: Sender display name
    :ivar MAIL_STARTTLS: Enable STARTTLS (default: True)
    :ivar MAIL_SSL_TLS: Enable SSL/TLS (default: False)
    :ivar USE_CREDENTIALS: Use SMTP credentials (default: True)
    :ivar VALIDATE_CERTS: Validate SSL certificates (default: True)
    :ivar CLOUDINARY_NAME: Cloudinary cloud name
    :ivar CLOUDINARY_API_KEY: Cloudinary API key
    :ivar CLOUDINARY_API_SECRET: Cloudinary API secret
    """

    DB_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600
    MAIL_USERNAME: EmailStr = "example@example.com"
    MAIL_PASSWORD: str = "xxxx xxxx xxxx xxxx"
    MAIL_FROM: EmailStr = "example@example.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_FROM_NAME: str = "Rest API Service"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    CLOUDINARY_NAME: str = "xxxxxxxxx"
    CLOUDINARY_API_KEY: str = "3123123123213"
    CLOUDINARY_API_SECRET: str = "31231231332"

    REDIS_URL: str = "redis://localhost:6379"

    ADMIN_EMAIL: str = "admin@example.com"

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()
