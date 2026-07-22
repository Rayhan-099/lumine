import pytest
import os
import tempfile
import io
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.core.config import Settings
from app.models.analysis import Analysis
from app.models.user import User
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_missing_secret_key_fails():
    os.environ["SECRET_KEY"] = ""
    with pytest.raises(ValueError, match="SECRET_KEY environment variable is missing or empty"):
        Settings()

def test_insecure_secret_key_fails():
    os.environ["SECRET_KEY"] = "supersecretkey_please_change_in_production"
    with pytest.raises(ValueError, match="SECRET_KEY is set to a known insecure placeholder"):
        Settings()

def test_short_secret_key_fails():
    os.environ["SECRET_KEY"] = "short_secret_123"
    with pytest.raises(ValueError, match="SECRET_KEY is too short"):
        Settings()

def test_valid_secret_key_succeeds():
    os.environ["SECRET_KEY"] = "a_very_long_and_secure_secret_key_that_is_32_chars+"
    settings = Settings()
    assert settings.SECRET_KEY == "a_very_long_and_secure_secret_key_that_is_32_chars+"

def test_oversized_upload_fails():
    # 11MB file
    large_content = b"a" * (11 * 1024 * 1024)
    response = client.post(
        "/analyze/",
        data={"description": "Test huge file"},
        files={"image": ("huge.jpg", large_content, "image/jpeg")}
    )
    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]

def test_invalid_image_format_rejected():
    response = client.post(
        "/analyze/",
        data={"description": "Test txt file"},
        files={"image": ("test.txt", b"hello world", "text/plain")}
    )
    assert response.status_code == 400
    assert "Invalid image format" in response.json()["detail"]

def test_corrupt_image_bytes_rejected():
    # Sending JPG content type but corrupt bytes
    response = client.post(
        "/analyze/",
        data={"description": "Test corrupt image"},
        files={"image": ("corrupt.jpg", b"not a real image", "image/jpeg")}
    )
    assert response.status_code == 400
    assert "Invalid or corrupt image" in response.json()["detail"]

def test_rate_limit_anonymous_analyze():
    # Need to simulate different IPs or just exhaust the limit
    # The limit is 3/hour
    for i in range(3):
        # We need a valid dummy image to pass initial validation and reach ML, but ML might fail.
        # Actually it's better to just send invalid images so we don't hit HF?
        # Wait, the rate limiter runs BEFORE route execution! So 400s count towards the limit.
        response = client.post(
            "/analyze/",
            data={"description": "Rate limit test"},
            files={"image": ("test.jpg", b"fakebytes", "image/jpeg")}
        )
        # Even if it's 400, it used quota!
    
    # The 4th request should be 429
    response = client.post(
        "/analyze/",
        data={"description": "Rate limit test"},
        files={"image": ("test.jpg", b"fakebytes", "image/jpeg")}
    )
    assert response.status_code == 429

def test_auth_leak_mitigated():
    # We don't have DB access in this simple test file to create a user, 
    # but we can try registering a dummy user twice and checking the error message.
    # We will use an email we know will either be created or already exists.
    email = "security_test@example.com"
    payload = {"email": email, "password": "TestPassword123!", "full_name": "Sec Test"}
    # first request
    res1 = client.post("/auth/register", json=payload)
    # second request
    res2 = client.post("/auth/register", json=payload)
    if res2.status_code == 400:
        assert "Registration failed. Please verify your information or try logging in." in res2.json()["detail"]

@patch("PIL.Image.open")
def test_image_dimensions_rejected(mock_image_open):
    app.state.limiter._storage.reset()
    # Mocking Image.open to return an image object with large dimensions
    mock_img = MagicMock()
    mock_img.size = (9000, 9000)
    mock_image_open.return_value = mock_img

    response = client.post(
        "/analyze/",
        data={"description": "Test large dimensions"},
        files={"image": ("test.jpg", b"fakebytes", "image/jpeg")},
        headers={"X-Forwarded-For": "9.9.9.1"}
    )
    assert response.status_code == 422
    assert "dimensions exceed" in response.json()["detail"]

@patch("PIL.Image.open")
def test_image_pixel_count_rejected(mock_image_open):
    app.state.limiter._storage.reset()
    # Dimensions under individual max, but total pixels > 20,000,000
    mock_img = MagicMock()
    mock_img.size = (5000, 5000) # 25M pixels
    mock_image_open.return_value = mock_img

    response = client.post(
        "/analyze/",
        data={"description": "Test large pixel count"},
        files={"image": ("test.jpg", b"fakebytes", "image/jpeg")},
        headers={"X-Forwarded-For": "9.9.9.2"}
    )
    assert response.status_code == 422
    assert "pixel count exceeds" in response.json()["detail"]

def test_ip_spoofing_resistance():
    # If a user spoofs X-Forwarded-For, the last IP should be extracted or direct client
    # First request
    response1 = client.post(
        "/analyze/",
        data={"description": "Spoof test 1"},
        files={"image": ("test.jpg", b"fake", "image/jpeg")},
        headers={"X-Forwarded-For": "8.8.8.8, 127.0.0.1"}
    )
    # The limiter uses the key function. Let's just make 3 requests with the same spoofing to exhaust quota for 127.0.0.1
    # Note: earlier tests might have exhausted the limit for 127.0.0.1 if we didn't reset it.
    app.state.limiter._storage.reset()
    
    for i in range(3):
        client.post(
            "/analyze/",
            data={"description": "Spoof test"},
            files={"image": ("test.jpg", b"fake", "image/jpeg")},
            headers={"X-Forwarded-For": f"1.2.3.{i}, 10.0.0.1"} # Spoofing the leftmost IP
        )
    
    # 4th request from same real client (10.0.0.1 is the last) should fail
    response = client.post(
        "/analyze/",
        data={"description": "Spoof test limit"},
        files={"image": ("test.jpg", b"fake", "image/jpeg")},
        headers={"X-Forwarded-For": "1.2.3.4, 10.0.0.1"}
    )
    assert response.status_code == 429

def test_jwt_bypass_fixed():
    app.state.limiter._storage.reset()
    
    # Send multiple requests with fake JWTs
    for i in range(3):
        client.post(
            "/analyze/",
            data={"description": "JWT test"},
            files={"image": ("test.jpg", b"fake", "image/jpeg")},
            headers={"Authorization": f"Bearer fake_token_{i}", "X-Forwarded-For": "10.0.0.2"}
        )
    
    # If the app trusted the raw token, each request would use a new bucket.
    # Since it falls back to IP (10.0.0.2) when JWT is invalid, the 4th request will be rate limited
    response = client.post(
        "/analyze/",
        data={"description": "JWT test limit"},
        files={"image": ("test.jpg", b"fake", "image/jpeg")},
        headers={"Authorization": "Bearer fake_token_4", "X-Forwarded-For": "10.0.0.2"}
    )
    assert response.status_code == 429
