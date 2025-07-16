"""
Test the home endpoint of the API.
"""

import pytest
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Fixture to create a test client for the FastAPI app."""
    return TestClient(app)


def test_home(client):
    """Test the home endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Authentication API!"}


def test_home_endpoint_returns_json(client):
    """Test that the home endpoint returns JSON content type."""
    response = client.get("/")
    assert response.headers["content-type"] == "application/json"


def test_home_endpoint_method_not_allowed(client):
    """Test that POST method is not allowed on home endpoint."""
    response = client.post("/")
    assert response.status_code == 405
