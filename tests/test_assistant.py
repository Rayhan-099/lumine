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

from app.services.llm_service import llm_service
from unittest.mock import MagicMock

class MockException(Exception):
    pass

@patch("time.sleep", return_value=None)
@patch.object(llm_service, "client")
def test_gemini_retry_503_success(mock_client, mock_sleep):
    mock_model = MagicMock()
    mock_client.models = mock_model
    
    success_response = MagicMock()
    success_response.text = "Success!"
    
    mock_model.generate_content.side_effect = [
        MockException("Service Unavailable: 503"),
        success_response
    ]
    
    result = llm_service._generate_with_retry("test prompt", "Fallback")
    
    assert result == "Success!"
    assert mock_model.generate_content.call_count == 2
    mock_sleep.assert_called_once()

@patch("time.sleep", return_value=None)
@patch.object(llm_service, "client")
def test_gemini_retry_503_fallback(mock_client, mock_sleep):
    mock_model = MagicMock()
    mock_client.models = mock_model
    
    mock_model.generate_content.side_effect = [
        MockException("Service Unavailable: 503"),
        MockException("Service Unavailable: 503"),
        MockException("Service Unavailable: 503")
    ]
    
    result = llm_service._generate_with_retry("test prompt", "Fallback")
    
    assert result == "Fallback"
    assert mock_model.generate_content.call_count == 3
    assert mock_sleep.call_count == 2

@patch("time.sleep", return_value=None)
@patch.object(llm_service, "client")
def test_gemini_retry_429_success(mock_client, mock_sleep):
    mock_model = MagicMock()
    mock_client.models = mock_model
    
    success_response = MagicMock()
    success_response.text = "Success!"
    
    mock_model.generate_content.side_effect = [
        MockException("Too Many Requests: 429"),
        success_response
    ]
    
    result = llm_service._generate_with_retry("test prompt", "Fallback")
    
    assert result == "Success!"
    assert mock_model.generate_content.call_count == 2
    mock_sleep.assert_called_once()

@patch("time.sleep", return_value=None)
@patch.object(llm_service, "client")
def test_gemini_no_retry_400(mock_client, mock_sleep):
    mock_model = MagicMock()
    mock_client.models = mock_model
    
    mock_model.generate_content.side_effect = [
        MockException("Bad Request: 400")
    ]
    
    result = llm_service._generate_with_retry("test prompt", "Fallback")
    
    assert result == "Fallback"
    assert mock_model.generate_content.call_count == 1
    mock_sleep.assert_not_called()

@patch("time.sleep", return_value=None)
@patch.object(llm_service, "client")
def test_gemini_empty_text_fallback(mock_client, mock_sleep):
    mock_model = MagicMock()
    mock_client.models = mock_model
    
    success_response = MagicMock()
    success_response.text = ""
    
    mock_model.generate_content.side_effect = [
        success_response,
        success_response,
        success_response
    ]
    
    result = llm_service._generate_with_retry("test prompt", "Fallback")
    
    assert result == "Fallback"
    assert mock_model.generate_content.call_count == 3
    assert mock_sleep.call_count == 0  # no transient sleep for missing text

@patch("app.services.llm_service.LLMService.generate_assistant_response")
def test_assistant_zero_history(mock_generate):
    class MockUser:
        id = 1
        email = "test@example.com"
    
    def override_get_current_user():
        return MockUser()
    
    mock_generate.return_value = "Hello! I am Lumine AI."
    
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
        json={"question": "What is a mole?"}
    )
    
    assert response.status_code == 200
    assert response.json()["answer"] == "Hello! I am Lumine AI."
    
    # Verify the prompt contained the zero history string
    args, kwargs = mock_generate.call_args
    assert "No verified previous skin analyses are available for this user." in args[0]
    
    app.dependency_overrides.clear()

@patch("time.sleep", return_value=None)
@patch.object(llm_service, "client")
def test_gemini_hard_quota_no_retry(mock_client, mock_sleep):
    mock_model = MagicMock()
    mock_client.models = mock_model
    
    mock_model.generate_content.side_effect = [
        MockException("429 RESOURCE_EXHAUSTED: GenerateRequestsPerDayPerProjectPerModel-FreeTier")
    ]
    
    result = llm_service._generate_with_retry("test prompt", "Fallback", quota_fallback_message="Quota Exceeded")
    
    assert result == "Quota Exceeded"
    assert mock_model.generate_content.call_count == 1
    mock_sleep.assert_not_called()

def test_assistant_local_greeting():
    class MockUser:
        id = 1
        email = "test@example.com"
    
    def override_get_current_user():
        return MockUser()
    
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
        json={"question": "hi"}
    )
    
    assert response.status_code == 200
    assert "Hi! I'm Lumine AI" in response.json()["answer"]
    
    app.dependency_overrides.clear()

