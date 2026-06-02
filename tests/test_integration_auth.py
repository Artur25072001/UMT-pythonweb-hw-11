from unittest.mock import Mock

import pytest
from sqlalchemy import select

from src.database.models import User
from src.services.auth import create_password_reset_token
from tests.conftest import TestingSessionLocal

user_data = {
    "username": "agent007",
    "email": "agent007@gmail.com",
    "password": "12345678",
}


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data
    assert "avatar" in data


def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Користувач з таким email вже існує"


def test_not_confirmed_login(client):
    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Електронна адреса не підтверджена"


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data


def test_wrong_password_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": user_data.get("username"), "password": "password"},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Неправильний логін або пароль"


def test_wrong_username_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": "username", "password": user_data.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Неправильний логін або пароль"


def test_validation_error_login(client):
    response = client.post(
        "api/auth/login", data={"password": user_data.get("password")}
    )
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data


# ===================== Forgot / Reset password =====================


def test_forgot_password(client, monkeypatch):
    """Should accept password reset request and send email."""
    mock_send_reset_email = Mock()
    monkeypatch.setattr("src.api.auth.send_password_reset_email", mock_send_reset_email)
    response = client.post(
        "api/auth/forgot-password",
        json={"email": user_data["email"]},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "message" in data
    mock_send_reset_email.assert_called_once()


def test_forgot_password_nonexistent_email(client, monkeypatch):
    """Should return success even for nonexistent email (prevent enumeration)."""
    mock_send_reset_email = Mock()
    monkeypatch.setattr("src.api.auth.send_password_reset_email", mock_send_reset_email)
    response = client.post(
        "api/auth/forgot-password",
        json={"email": "nonexistent@example.com"},
    )
    assert response.status_code == 200, response.text
    mock_send_reset_email.assert_not_called()


@pytest.mark.asyncio
async def test_reset_password(client):
    """Should reset password using a valid token and allow login with new password."""
    user_email = user_data["email"]
    token = create_password_reset_token({"sub": user_email})
    new_password = "newpassword123"

    response = client.post(
        f"api/auth/reset-password/{token}",
        json={"token": token, "new_password": new_password},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Пароль успішно змінено"

    # Try logging in with the new password
    response = client.post(
        "api/auth/login",
        data={"username": user_data["username"], "password": new_password},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data


def test_reset_password_invalid_token(client):
    """Should return 422 for an invalid token."""
    response = client.post(
        "api/auth/reset-password/invalid_token_here",
        json={"token": "invalid_token_here", "new_password": "newpass123"},
    )
    assert response.status_code == 422, response.text


def test_reset_password_user_not_found(client):
    """Should return 400 when the user does not exist."""
    from src.services.auth import create_password_reset_token

    token = create_password_reset_token({"sub": "nonexistent@example.com"})
    response = client.post(
        f"api/auth/reset-password/{token}",
        json={"token": token, "new_password": "newpass123"},
    )
    assert response.status_code == 400, response.text


def test_confirmed_email_already_confirmed(client, get_token):
    """Should return message when email is already confirmed."""
    # The test user is already confirmed in conftest
    from src.services.auth import create_email_token

    token = create_email_token({"sub": "deadpool@example.com"})  # confirmed user
    response = client.get(f"api/auth/confirmed_email/{token}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert (
        "вже підтверджена" in data["message"] or "already confirmed" in data["message"]
    )


def test_confirmed_email_invalid_token(client):
    """Should return 422 for an invalid confirmation token."""
    response = client.get("api/auth/confirmed_email/invalid_token_here")
    assert response.status_code == 422, response.text


def test_forgot_password_returns_message(client):
    """Should return proper message structure."""
    response = client.post(
        "api/auth/forgot-password",
        json={"email": "test@example.com"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "message" in data
