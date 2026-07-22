import requests
import os
from app.core.config import settings
from fastapi import UploadFile
from app.core.logging import logger

class MLService:
    @staticmethod
    def get_condition_details(label: str) -> dict:
        """
        Returns structured educational details ONLY for valid ML predictions.
        Does NOT invent predictions from raw user text.
        """
        label_lower = label.lower()
        
        if "melanoma" in label_lower or "malignant" in label_lower or "carcinoma" in label_lower:
            return {
                "condition": label,
                "causes": "May be related to UV exposure or genetic factors.",
                "suggestion": "Possible serious lesion. Consult a certified dermatologist immediately.",
                "seriousness": "high"
            }
        elif "eczema" in label_lower or "dermatitis" in label_lower:
            return {
                "condition": label,
                "causes": "Skin barrier dysfunction, allergens, or irritants.",
                "suggestion": "Use gentle moisturizers and avoid known triggers.",
                "seriousness": "medium"
            }
        elif "acne" in label_lower or "rosacea" in label_lower:
            return {
                "condition": label,
                "causes": "Clogged pores, excess oil, or bacterial inflammation.",
                "suggestion": "Cleanse twice daily with a mild cleanser and avoid touching the area.",
                "seriousness": "low"
            }
        elif "fungal" in label_lower or "tinea" in label_lower or "ringworm" in label_lower:
            return {
                "condition": label,
                "causes": "Fungal overgrowth, often in warm or moist areas.",
                "suggestion": "Keep the area dry and consider over-the-counter antifungal creams.",
                "seriousness": "medium"
            }
        elif "psoriasis" in label_lower:
            return {
                "condition": label,
                "causes": "Autoimmune response accelerating skin cell turnover.",
                "suggestion": "Moisturize regularly and consult a doctor for flare-ups.",
                "seriousness": "medium"
            }
        else:
            return {
                "condition": label,
                "causes": "Unknown or general skin variation.",
                "suggestion": "Monitor the condition. Consult a doctor if symptoms worsen.",
                "seriousness": "unknown"
            }

    @staticmethod
    async def analyze_image(image: UploadFile) -> dict:
        try:
            img_bytes = await image.read()
            # Restoring original intended model for skin diseases
            model_id = os.getenv("HF_IMAGE_MODEL", "dima806/skin-disease-classification")
            image_model_url = f"https://api-inference.huggingface.co/models/{model_id}"
            headers = {"Authorization": f"Bearer {settings.HF_TOKEN}"}

            response = requests.post(image_model_url, headers=headers, data=img_bytes, timeout=40)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    top = result[0]
                    return {
                        "predicted_label": top.get("label", "Unknown"),
                        "confidence": round(top.get("score", 0) * 100, 2),
                        "status": "success",
                        "model_id": model_id
                    }
                else:
                    logger.error(f"HF Inference: No valid predictions returned. Response: {result}")
                    raise ValueError("No valid predictions returned from HF model.")
            else:
                logger.error(f"HF Inference API failed: Status {response.status_code}, Body: {response.text}")
                raise ConnectionError(f"HF API failed with status {response.status_code}")

        except Exception as e:
            logger.error(f"Hugging Face unavailable, inference failed: {str(e)}")
            return {
                "predicted_label": "Analysis Unavailable",
                "confidence": 0.0,
                "status": "error",
                "error": "Image inference failed or is currently unavailable."
            }
