import pytest
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

# Basic sanity tests for the E2E framework

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Lumine API"}

def test_register_and_login():
    # Register
    register_data = {
        "email": "test_e2e@example.com",
        "password": "securepassword",
        "full_name": "Test User"
    }
    response = client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code in (200, 400) # 400 if already exists

    # Login
    login_data = {
        "username": "test_e2e@example.com",
        "password": "securepassword"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    
    token = response.json()["access_token"]
    
    # Get Me
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "test_e2e@example.com"
