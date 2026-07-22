import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
from app.api.deps import get_db
import app.models.user
from app.core import security
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

from sqlalchemy.pool import StaticPool

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(setup_database):
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

def test_register_normal(client):
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "password123", "full_name": "Test User"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "hashed_password" not in data
    assert "password" not in data

def test_register_duplicate(client):
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "password123", "full_name": "Test User"}
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_login_correct(client):
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_incorrect(client):
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect email or password"

def test_register_long_password(client):
    long_password = "a" * 73
    response = client.post(
        "/auth/register",
        json={"email": "long@example.com", "password": long_password, "full_name": "Long Password"}
    )
    assert response.status_code == 400
    assert "max 72 bytes" in response.json()["detail"]

def test_register_unicode_password(client):
    unicode_password = "pāsswörd"
    response = client.post(
        "/auth/register",
        json={"email": "unicode@example.com", "password": unicode_password, "full_name": "Unicode"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "unicode@example.com"
    
    # login
    login_response = client.post(
        "/auth/login",
        data={"username": "unicode@example.com", "password": unicode_password}
    )
    assert login_response.status_code == 200

def test_verify_password_malformed_hash():
    # Directly test the verification function with a malformed hash
    assert security.verify_password("password", "invalid_hash_format") == False
    assert security.verify_password("password", "") == False
    assert security.verify_password("password", None) == False

def test_password_is_hashed():
    password = "secretpassword"
    hashed = security.get_password_hash(password)
    assert hashed != password
    assert isinstance(hashed, str)
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
