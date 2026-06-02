"""
Integration tests for contact API routes.

Uses the SQLite test database and TestClient defined in conftest.
All endpoints require authentication unless stated otherwise.
"""

import pytest
from sqlalchemy import select

from src.database.models import Contact
from tests.conftest import (
    TestingSessionLocal,
    test_user,
    admin_user,
)

contact_data = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "birthday": "1990-01-15",
}

updated_contact_data = {
    "first_name": "John",
    "last_name": "Smith",
    "email": "john.smith@example.com",
    "phone": "+0987654321",
    "birthday": "1991-02-20",
}


def test_create_contact(client, get_token):
    """Should create a new contact for the authenticated user."""
    response = client.post(
        "api/contacts/",
        json=contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["first_name"] == contact_data["first_name"]
    assert data["last_name"] == contact_data["last_name"]
    assert data["email"] == contact_data["email"]
    assert "id" in data


def test_get_contacts(client, get_token):
    """Should return list of contacts for the authenticated user."""
    response = client.get(
        "api/contacts/",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) >= 1
    assert data[0]["email"] == contact_data["email"]


def test_get_contact_by_id(client, get_token):
    """Should return a specific contact by ID."""
    # First get all contacts to find the created one's ID
    list_response = client.get(
        "api/contacts/",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    contact_id = list_response.json()[0]["id"]

    response = client.get(
        f"api/contacts/{contact_id}",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == contact_id
    assert data["email"] == contact_data["email"]


def test_get_contact_not_found(client, get_token):
    """Should return 404 when contact does not exist."""
    response = client.get(
        "api/contacts/99999",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404, response.text


def test_update_contact(client, get_token):
    """Should update an existing contact."""
    list_response = client.get(
        "api/contacts/",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    contact_id = list_response.json()[0]["id"]

    response = client.put(
        f"api/contacts/{contact_id}",
        json=updated_contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["last_name"] == updated_contact_data["last_name"]
    assert data["email"] == updated_contact_data["email"]


def test_delete_contact(client, get_token):
    """Should delete an existing contact."""
    list_response = client.get(
        "api/contacts/",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    contact_id = list_response.json()[0]["id"]

    response = client.delete(
        f"api/contacts/{contact_id}",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 204, response.text

    # Verify it's gone
    get_response = client.get(
        f"api/contacts/{contact_id}",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert get_response.status_code == 404


def test_create_contact_unauthenticated(client):
    """Should return 401 when no token is provided."""
    response = client.post(
        "api/contacts/",
        json=contact_data,
    )
    assert response.status_code == 401, response.text


def test_get_contacts_unauthenticated(client):
    """Should return 401 when no token is provided."""
    response = client.get("api/contacts/")
    assert response.status_code == 401, response.text
