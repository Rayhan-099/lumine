import os
import requests
import json

HF_TOKEN = os.getenv("HF_TOKEN")
HF_IMAGE_MODEL = os.getenv("HF_IMAGE_MODEL", "dima806/skin-disease-classification")

def analyze_image(image_path: str):
    """
    Use Hugging Face pretrained skin-disease model.
    """
    if not HF_TOKEN:
        return {"error": "Hugging Face token missing"}

    url = f"https://api-inference.huggingface.co/models/{HF_IMAGE_MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    with open(image_path, "rb") as f:
        img_bytes = f.read()

    try:
        response = requests.post(url, headers=headers, data=img_bytes, timeout=40)
    except Exception as e:
        return {"error": f"Network error: {e}"}

    if response.status_code != 200:
        return {"error": f"Hugging Face error {response.status_code}: {response.text}"}

    try:
        data = response.json()
    except json.JSONDecodeError:
        return {"error": "Invalid JSON from model"}

    if not isinstance(data, list) or len(data) == 0:
        return {"error": "Unexpected model output"}

    top = data[0]
    label = top.get("label", "unknown")
    confidence = round(top.get("score", 0.0) * 100, 2)

    seriousness = "low"
    suggestion = "Follow general skincare routine and consult if needed."

    if "melanoma" in label.lower() or "malignant" in label.lower():
        seriousness = "high"
        suggestion = "Possible serious lesion. Consult dermatologist immediately."
    elif "eczema" in label.lower():
        seriousness = "medium"
        suggestion = "Use moisturizer and avoid irritants."
    elif "acne" in label.lower():
        seriousness = "low"
        suggestion = "Cleanse twice daily with mild cleanser."
    elif "fungal" in label.lower():
        seriousness = "medium"
        suggestion = "Keep area dry, apply antifungal cream."
    elif "psoriasis" in label.lower():
        seriousness = "medium"
        suggestion = "Moisturize often; consult if persistent."

    return {
        "possible_condition": label,
        "confidence": f"{confidence}%",
        "suggestion": suggestion,
        "seriousness_level": seriousness
    }
