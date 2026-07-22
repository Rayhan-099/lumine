import requests
import random
from app.core.config import settings
from fastapi import UploadFile

class MLService:
    @staticmethod
    def analyze_text(description: str) -> dict:
        desc_lower = description.lower()
        if any(word in desc_lower for word in ["acne", "pimple", "zit", "oily skin"]):
            return {
                "condition": "Acne",
                "causes": "Clogged pores and excess oil production.",
                "suggestion": "Use a mild oil-free cleanser and avoid touching your face.",
                "seriousness": "low"
            }
        elif any(word in desc_lower for word in ["rash", "rashes", "itching", "irritation", "allergy", "red spots"]):
            return {
                "condition": "Skin Rash or Allergy",
                "causes": "Reaction to allergens, heat, or sweat.",
                "suggestion": "Apply calamine lotion or hydrocortisone cream. Keep area clean.",
                "seriousness": "medium"
            }
        elif any(word in desc_lower for word in ["scar", "mark", "wound", "injury", "cut", "bruise"]):
            return {
                "condition": "Skin or Body Scar",
                "causes": "Post-injury or acne marks on skin/body.",
                "suggestion": "Use scar-reducing cream and moisturize regularly.",
                "seriousness": "low"
            }
        elif any(word in desc_lower for word in ["burn", "burnt", "blister"]):
            return {
                "condition": "Skin Burn",
                "causes": "Thermal or chemical damage to skin layers.",
                "suggestion": "Cool the area with water, avoid breaking blisters, and use burn cream.",
                "seriousness": "high"
            }
        elif any(word in desc_lower for word in ["dry", "flaky", "rough skin"]):
            return {
                "condition": "Dry Skin",
                "causes": "Dehydration or lack of moisture.",
                "suggestion": "Use moisturizer regularly and avoid hot showers.",
                "seriousness": "low"
            }
        else:
            return {
                "condition": "Unclear",
                "causes": "Could not determine based on text alone.",
                "suggestion": "Consider uploading an image for better detection.",
                "seriousness": "unknown"
            }

    @staticmethod
    async def analyze_image(image: UploadFile) -> dict:
        try:
            img_bytes = await image.read()
            image_model_url = "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"
            headers = {"Authorization": f"Bearer {settings.HF_TOKEN}"}

            response = requests.post(image_model_url, headers=headers, data=img_bytes)
            print("HF Status:", response.status_code)

            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    top = result[0]
                    return {
                        "predicted_label": top.get("label", "Unknown Object"),
                        "confidence": round(top.get("score", 0) * 100, 2),
                        "mode": "Hugging Face Model"
                    }
                else:
                    raise ValueError("No valid predictions returned from HF model.")
            else:
                raise ConnectionError(f"HF API failed with status {response.status_code}")

        except Exception as e:
            print("⚠️ Hugging Face unavailable, inference failed:", e)
            return {
                "predicted_label": "Analysis Unavailable",
                "confidence": 0.0,
                "mode": "Service Unavailable",
                "error": "Image inference failed or is currently unavailable."
            }
