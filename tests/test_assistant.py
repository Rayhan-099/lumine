import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.core import security

# We can reuse the setup_database fixture from test_auth if needed,
# but for the assistant endpoint testing the LLM logic, we can mock it directly.

client = TestClient(app)

@patch("app.services.llm_service.LLMService.generate_assistant_response")
def test_assistant_successful_mocked_response(mock_generate):
    class MockUser:
        id = 1
        email = "test@example.com"
    
    def override_get_current_user():
        return MockUser()
        
    mock_generate.return_value = "Yes, you should apply sunscreen daily."
    
    from app.api.deps import get_db, get_current_user
    from unittest.mock import MagicMock

    def override_get_db():
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    response = client.post(
        "/assistant/ask",
        json={"question": "Should I apply sunscreen?"}
    )
    
    assert response.status_code == 200
    assert response.json()["answer"] == "Yes, you should apply sunscreen daily."
    
    app.dependency_overrides.clear()

@patch("app.services.llm_service.LLMService.generate_assistant_response")
def test_assistant_llm_failure_handled_gracefully(mock_generate):
    class MockUser:
        id = 1
        email = "test@example.com"
    
    def override_get_current_user():
        return MockUser()
    
    mock_generate.return_value = "I'm sorry, I couldn't process your request right now due to a service interruption."
    
    from app.api.deps import get_db, get_current_user
    from unittest.mock import MagicMock

    def override_get_db():
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    response = client.post(
        "/assistant/ask",
        json={"question": "Why is my skin dry?"}
    )
    
    assert response.status_code == 200
    assert "service interruption" in response.json()["answer"]
    
    app.dependency_overrides.clear()
