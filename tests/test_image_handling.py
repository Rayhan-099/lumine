import pytest
import io
from PIL import Image
from unittest.mock import patch, MagicMock
from fastapi import UploadFile
from app.services.ml_service import MLService

def create_mock_upload_file(image_mode="RGB", image_format="JPEG"):
    img = Image.new(image_mode, (224, 224), color=(255, 204, 204))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format=image_format)
    img_byte_arr.seek(0)
    return UploadFile(filename=f"test.{image_format.lower()}", file=img_byte_arr)

@pytest.mark.asyncio
@patch("app.services.ml_service.InferenceClient")
async def test_jpeg_reaches_inference(MockInferenceClient):
    mock_client_instance = MockInferenceClient.return_value
    mock_client_instance.image_classification.return_value = [{"label": "melanoma", "score": 0.99}]
    
    upload_file = create_mock_upload_file(image_format="JPEG")
    res = await MLService.analyze_image(upload_file)
    
    assert res["status"] == "success"
    # Verify the mock was called with bytes
    called_args = mock_client_instance.image_classification.call_args[0]
    assert len(called_args) == 1
    passed_bytes = called_args[0]
    assert isinstance(passed_bytes, bytes)
    
    # Verify the bytes sent are actually a valid JPEG
    sent_img = Image.open(io.BytesIO(passed_bytes))
    assert sent_img.format == "JPEG"

@pytest.mark.asyncio
@patch("app.services.ml_service.InferenceClient")
async def test_png_reaches_inference_as_jpeg(MockInferenceClient):
    mock_client_instance = MockInferenceClient.return_value
    mock_client_instance.image_classification.return_value = [{"label": "eczema", "score": 0.88}]
    
    upload_file = create_mock_upload_file(image_format="PNG")
    res = await MLService.analyze_image(upload_file)
    
    assert res["status"] == "success"
    passed_bytes = mock_client_instance.image_classification.call_args[0][0]
    sent_img = Image.open(io.BytesIO(passed_bytes))
    assert sent_img.format == "JPEG"  # MLService should encode all to JPEG for the API

@pytest.mark.asyncio
@patch("app.services.ml_service.InferenceClient")
async def test_rgba_image_handled_correctly(MockInferenceClient):
    mock_client_instance = MockInferenceClient.return_value
    mock_client_instance.image_classification.return_value = [{"label": "psoriasis", "score": 0.90}]
    
    # RGBA must be converted to RGB before saving as JPEG
    upload_file = create_mock_upload_file(image_mode="RGBA", image_format="PNG")
    res = await MLService.analyze_image(upload_file)
    
    assert res["status"] == "success"
    passed_bytes = mock_client_instance.image_classification.call_args[0][0]
    sent_img = Image.open(io.BytesIO(passed_bytes))
    assert sent_img.format == "JPEG"
    assert sent_img.mode == "RGB"

@pytest.mark.asyncio
@patch("app.services.ml_service.InferenceClient")
async def test_invalid_image_bytes_rejected(MockInferenceClient):
    mock_client_instance = MockInferenceClient.return_value
    
    upload_file = UploadFile(filename="bad.txt", file=io.BytesIO(b"this is not an image"))
    res = await MLService.analyze_image(upload_file)
    
    assert res["status"] == "error"
    assert res["error"] == "Invalid image format uploaded."
    assert res["confidence"] == 0.0
    mock_client_instance.image_classification.assert_not_called()

@pytest.mark.asyncio
@patch("app.services.ml_service.InferenceClient")
async def test_provider_bad_request_error_returns_controlled_failure(MockInferenceClient):
    from huggingface_hub.utils import BadRequestError
    import requests
    
    mock_client_instance = MockInferenceClient.return_value
    mock_response = requests.Response()
    mock_response.status_code = 400
    mock_response.reason = "Bad Request"
    mock_client_instance.image_classification.side_effect = BadRequestError("No content type provided", response=mock_response)
    
    upload_file = create_mock_upload_file(image_format="JPEG")
    res = await MLService.analyze_image(upload_file)
    
    assert res["status"] == "error"
    assert "Image inference failed" in res["error"]
    assert res["confidence"] == 0.0
