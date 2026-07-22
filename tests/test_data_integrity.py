import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.analysis import Analysis
from app.main import app
from datetime import datetime
from sqlalchemy.pool import StaticPool
import json
from unittest.mock import patch, MagicMock

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Create test user
    test_user = User(id=1, email="test_integrity@example.com", hashed_password="fake")
    db.add(test_user)
    db.commit()

    # Create 1 Valid Analysis
    valid_analysis = Analysis(
        user_id=1,
        predicted_class="Melanoma",
        confidence=95.5,
        text_condition="Melanoma",
        text_seriousness="consult_doctor",
        inference_status="success",
        timestamp=datetime.now()
    )
    db.add(valid_analysis)

    # Create 1 Fake/Contaminated Analysis (0% confidence)
    fake_analysis = Analysis(
        user_id=1,
        predicted_class="Skin Rash or Allergy",
        confidence=0.0,
        text_condition="Skin Rash or Allergy",
        text_seriousness="unknown",
        inference_status="legacy_unverified",
        timestamp=datetime.now()
    )
    db.add(fake_analysis)
    db.commit()
    
    yield
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(setup_database):
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
            
    def override_get_current_user():
        db = TestingSessionLocal()
        return db.query(User).filter(User.id == 1).first()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.state.limiter.enabled = False
    with TestClient(app) as c:
        yield c
    app.state.limiter.enabled = True
    app.dependency_overrides.clear()

def test_trends_ignores_zero_confidence(client):
    response = client.get("/history/trends/")
    assert response.status_code == 200
    data = response.json()
    
    # Even though there are 2 records in DB, only 1 should be counted
    assert data["total_analyses"] == 1
    assert data["most_frequent_concern"] == "Melanoma"
    
    # The timeline should not contain the fake condition
    conditions = [item["condition"] for item in data["timeline"]]
    assert "Melanoma" in conditions
    assert "Skin Rash or Allergy" not in conditions

@patch("app.services.llm_service.LLMService.generate_assistant_response")
def test_assistant_ignores_invalid_inferences(mock_generate, client):
    # Mocking LLM so it doesn't make external call
    mock_generate.return_value = "Assistant Response"
    
    response = client.post(
        "/assistant/ask",
        json={"question": "What is my history?"}
    )
    assert response.status_code == 200
    
    # Verify the prompt passed to the LLM does not contain the fake condition
    call_args = mock_generate.call_args[0][0]
    assert "Melanoma" in call_args
    assert "Skin Rash or Allergy" not in call_args

@patch("PIL.Image.open")
@patch("app.services.ml_service.MLService.analyze_image")
@patch("app.services.llm_service.LLMService.generate_report")
def test_failed_inference_not_persisted(mock_generate, mock_analyze, mock_image_open, client):
    mock_img = MagicMock()
    mock_img.size = (100, 100)
    mock_image_open.return_value = mock_img
    mock_analyze.return_value = {
        "predicted_label": "Analysis Unavailable",
        "confidence": 0.0,
        "status": "error",
        "error": "Failed"
    }
    mock_generate.return_value = "Failed"

    response = client.post(
        "/analyze/",
        data={"description": "Test failed inference"},
        files={"image": ("test.jpg", b"fakebytes", "image/jpeg")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    
    # Verify it was not saved by checking trends again (should still be 1 total)
    trends_response = client.get("/history/trends/")
    assert trends_response.json()["total_analyses"] == 1
