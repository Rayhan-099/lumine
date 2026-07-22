import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

@patch("app.services.ml_service.MLService.analyze_image")
@patch("app.services.llm_service.LLMService.generate_report")
def test_successful_inference(mock_generate_report, mock_analyze_image):
    # Mocking MLService success
    mock_analyze_image.return_value = {
        "predicted_label": "melanoma",
        "confidence": 95.5,
        "status": "success",
        "model_id": "Jayanth2002/dinov2-base-finetuned-SkinDisease",
        "top_predictions": [{"label": "melanoma", "score": 95.5}, {"label": "nevus", "score": 2.0}],
        "is_ambiguous": False
    }
    
    # Mocking LLM success
    mock_generate_report.return_value = "This looks like a valid model prediction. Please consult a doctor."

    response = client.post(
        "/analyze/",
        data={"description": "I have a dark spot."},
        files={"image": ("test.jpg", b"fake_image_bytes", "image/jpeg")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["image_analysis"]["predicted_label"] == "melanoma"
    assert data["text_analysis"]["condition"] == "melanoma"
    assert data["text_analysis"]["educational_action_level"] == "consult_doctor"
    assert data["ai_summary"] == "This looks like a valid model prediction. Please consult a doctor."
    assert "potentially serious condition" in data["recommendation"]

@patch("app.services.ml_service.MLService.analyze_image")
@patch("app.services.llm_service.LLMService.generate_report")
def test_inference_failure_no_fake_condition(mock_generate_report, mock_analyze_image):
    # Mocking MLService failure
    mock_analyze_image.return_value = {
        "predicted_label": "Analysis Unavailable",
        "confidence": 0.0,
        "status": "error",
        "error": "Image inference failed or is currently unavailable."
    }
    
    response = client.post(
        "/analyze/",
        data={"description": "I have a rash"},
        files={"image": ("test.jpg", b"fake_image_bytes", "image/jpeg")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert data["text_analysis"] is None  # IMPORTANT: No fake condition is generated
    assert data["recommendation"] is None
    assert data["image_analysis"]["predicted_label"] == "Analysis Unavailable"

@patch("app.services.ml_service.MLService.analyze_image")
@patch("app.services.llm_service.LLMService.generate_report")
def test_gemini_failure_does_not_destroy_ml_result(mock_generate_report, mock_analyze_image):
    mock_analyze_image.return_value = {
        "predicted_label": "psoriasis",
        "confidence": 88.0,
        "status": "success",
        "model_id": "Jayanth2002/dinov2-base-finetuned-SkinDisease",
        "top_predictions": [{"label": "psoriasis", "score": 88.0}],
        "is_ambiguous": False
    }
    
    # Mocking LLM failure response string
    mock_generate_report.return_value = "AI insights are temporarily unavailable. Your analysis results are unaffected."

    response = client.post(
        "/analyze/",
        data={"description": "My skin is itchy"},
        files={"image": ("test.jpg", b"fake_image_bytes", "image/jpeg")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "partial_success"
    assert data["image_analysis"]["predicted_label"] == "psoriasis"
    assert data["text_analysis"]["condition"] == "psoriasis"
    assert "unavailable" in data["ai_summary"]

@patch("app.services.ml_service.MLService.analyze_image")
@patch("app.services.llm_service.LLMService.generate_report")
def test_unknown_model_label_behavior(mock_generate_report, mock_analyze_image):
    mock_analyze_image.return_value = {
        "predicted_label": "totally_new_disease_123",
        "confidence": 99.0,
        "status": "success",
        "model_id": "Jayanth2002/dinov2-base-finetuned-SkinDisease",
        "top_predictions": [{"label": "totally_new_disease_123", "score": 99.0}],
        "is_ambiguous": False
    }
    mock_generate_report.return_value = "Summary."
    
    response = client.post(
        "/analyze/",
        data={"description": "My skin is itchy"},
        files={"image": ("test.jpg", b"fake_image_bytes", "image/jpeg")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["image_analysis"]["predicted_label"] == "totally_new_disease_123"
    assert data["text_analysis"]["condition"] == "totally_new_disease_123"
    assert data["text_analysis"]["educational_action_level"] == "unknown"
    assert "unavailable" in data["text_analysis"]["suggestion"]
