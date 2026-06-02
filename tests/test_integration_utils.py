"""
Integration tests for utility API routes.
"""

from tests.conftest import test_user


def test_healthchecker(client):
    """Should return health check message when database is reachable."""
    response = client.get("api/healthchecker")
    assert response.status_code == 200, response.text
    data = response.json()
    assert "message" in data
