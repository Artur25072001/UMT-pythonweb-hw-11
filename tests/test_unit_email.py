"""
Unit tests for the email sending service.
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest


@pytest.fixture
def mock_fastmail():
    """Patch FastMail so no real emails are sent."""
    with patch("src.services.email.FastMail") as mock:
        mock_instance = MagicMock()
        mock_instance.send_message = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance


def _extract_email(recipient) -> str:
    """Return the plain email address from a NameEmail object or a string."""
    return recipient.email if hasattr(recipient, "email") else str(recipient)


@pytest.mark.asyncio
async def test_send_email_success(mock_fastmail):
    """Should create a token and send an email confirmation."""
    from src.services.email import send_email

    await send_email(
        email="test@example.com",
        username="testuser",
        host="http://testhost/",
    )

    mock_fastmail.send_message.assert_awaited_once()
    call_args = mock_fastmail.send_message.await_args
    message = call_args[0][0]

    assert message.subject == "Confirm your email"
    # fastapi-mail wraps strings in NameEmail — compare the .email attribute
    assert [_extract_email(r) for r in message.recipients] == ["test@example.com"]
    assert message.template_body["host"] == "http://testhost/"
    assert message.template_body["username"] == "testuser"
    assert "token" in message.template_body


@pytest.mark.asyncio
async def test_send_email_error_handled(mock_fastmail):
    """Should catch and log exceptions without propagating them."""
    mock_fastmail.send_message.side_effect = Exception("SMTP error")

    from src.services.email import send_email

    # Should not raise
    await send_email(
        email="test@example.com",
        username="testuser",
        host="http://testhost/",
    )


@pytest.mark.asyncio
async def test_send_password_reset_email_success(mock_fastmail):
    """Should send a password reset email."""
    from src.services.email import send_password_reset_email

    await send_password_reset_email(
        email="test@example.com",
        username="testuser",
        host="http://testhost/",
    )

    mock_fastmail.send_message.assert_awaited_once()
    call_args = mock_fastmail.send_message.await_args
    message = call_args[0][0]

    assert message.subject == "Password Reset"
    # fastapi-mail wraps strings in NameEmail — compare the .email attribute
    assert [_extract_email(r) for r in message.recipients] == ["test@example.com"]
    assert message.template_body["username"] == "testuser"
    assert "token" in message.template_body


@pytest.mark.asyncio
async def test_send_password_reset_email_error(mock_fastmail):
    """Should catch and log password reset email errors."""
    mock_fastmail.send_message.side_effect = Exception("SMTP error")

    from src.services.email import send_password_reset_email

    await send_password_reset_email(
        email="test@example.com",
        username="testuser",
        host="http://testhost/",
    )
