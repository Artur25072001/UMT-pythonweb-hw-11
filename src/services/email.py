"""
Email sending service.

This module handles email sending functionality, including
confirmation email generation and delivery using FastMail.

:author: Artur
:version: 1.0.0
"""

from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import create_email_token, create_password_reset_token
from src.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    Send an email confirmation message to a user.

    Generates a verification token and sends an HTML email with a
    confirmation link to the specified email address.

    :param email: Recipient's email address
    :type email: EmailStr
    :param username: Recipient's username for personalization
    :type username: str
    :param host: Base URL of the application for the confirmation link
    :type host: str
    :return: None
    :rtype: None
    """
    try:
        token_verification = create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        print("Sending email...")
        print(f"Email: {email}, Username: {username}, Host: {host}")
        await fm.send_message(message, template_name="verify_email.html")
    except Exception as err:
        print(f"EMAIL ERROR: {err}")


async def send_password_reset_email(email: EmailStr, username: str, host: str):
    """
    Send a password reset email to a user.

    Generates a short-lived JWT token and sends an HTML email with a
    password reset link to the specified email address.

    :param email: Recipient's email address
    :type email: EmailStr
    :param username: Recipient's username for personalization
    :type username: str
    :param host: Base URL of the application for the reset link
    :type host: str
    :return: None
    :rtype: None
    """
    try:
        token_verification = create_password_reset_token({"sub": email})
        message = MessageSchema(
            subject="Password Reset",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        print("Sending password reset email...")
        print(f"Email: {email}, Username: {username}, Host: {host}")
        await fm.send_message(message, template_name="reset_password.html")
    except Exception as err:
        print(f"PASSWORD RESET EMAIL ERROR: {err}")
