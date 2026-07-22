import os
from app.core.config import settings
from fastapi import UploadFile
from app.core.logging import logger
from huggingface_hub import InferenceClient

class MLService:
    @staticmethod
    def get_condition_details(label: str) -> dict:
        """
        Returns structured educational details ONLY for valid ML predictions.
        Does NOT invent predictions from raw user text.
        """
        label_lower = label.lower()
        
        # High seriousness / Cancerous
        if any(term in label_lower for term in ["melanoma", "carcinoma"]):
            return {
                "condition": label,
                "causes": "May be related to UV exposure or genetic factors.",
                "suggestion": "Possible serious lesion. Consult a certified dermatologist immediately.",
                "seriousness": "high"
            }
            
        # Inflammatory / Autoimmune / Eczema / Psoriasis
        elif any(term in label_lower for term in ["eczema", "dermatitis", "psoriasis", "lupus", "lichen", "darier"]):
            return {
                "condition": label,
                "causes": "Skin barrier dysfunction, autoimmune response, or irritants.",
                "suggestion": "Moisturize regularly and consult a doctor for flare-ups.",
                "seriousness": "medium"
            }
            
        # Acne / Rosacea
        elif "acne" in label_lower or "rosacea" in label_lower:
            return {
                "condition": label,
                "causes": "Clogged pores, excess oil, or bacterial inflammation.",
                "suggestion": "Cleanse twice daily with a mild cleanser and avoid touching the area.",
                "seriousness": "low"
            }
            
        # Infections (Fungal, Bacterial, Viral, Parasitic)
        elif any(term in label_lower for term in ["tinea", "fungal", "ringworm", "herpes", "impetigo", "leprosy", "pediculosis", "larva", "tungiasis", "molluscum"]):
            return {
                "condition": label,
                "causes": "Infection by fungus, bacteria, virus, or parasite.",
                "suggestion": "Maintain hygiene and consult a doctor for appropriate antimicrobial treatment.",
                "seriousness": "medium"
            }
            
        # Benign Lesions (Keratosis, Nevus, Dermatofibroma, etc.)
        elif any(term in label_lower for term in ["keratosis", "nevus", "dermatofibroma", "vascular lesion", "papilomatosis"]):
            # Actinic keratosis is precancerous, bump seriousness
            if "actinic" in label_lower:
                return {
                    "condition": label,
                    "causes": "Precancerous growth caused by sun damage.",
                    "suggestion": "Monitor closely and consult a dermatologist for removal options.",
                    "seriousness": "medium"
                }
            return {
                "condition": label,
                "causes": "Often a harmless benign growth or pigmentation.",
                "suggestion": "Monitor the condition for any changes in size, shape, or color.",
                "seriousness": "low"
            }
            
        else:
            return {
                "condition": label,
                "causes": "Unknown or general skin variation.",
                "suggestion": "Monitor the condition. Consult a doctor if symptoms worsen.",
                "seriousness": "unknown"
            }

    @staticmethod
    def check_inference_status():
        hf_token = getattr(settings, "HF_TOKEN", os.getenv("HF_TOKEN"))
        model_id = os.getenv("HF_IMAGE_MODEL", "Jayanth2002/dinov2-base-finetuned-SkinDisease")
        
        logger.info(f"ML Diagnostics: HF token configured: {bool(hf_token)}")
        logger.info(f"ML Diagnostics: HF inference model: {model_id}")
        
        if not hf_token:
            logger.warning("ML Diagnostics: HF_TOKEN is missing. Image analysis will fail.")
            return

        try:
            client = InferenceClient(model=model_id, token=hf_token)
            # Cannot do a full dummy image ping without an image, but we check init
            logger.info("ML Diagnostics: HF InferenceClient initialized successfully.")
        except Exception as e:
            logger.error(f"ML Diagnostics: Failed to initialize InferenceClient for model {model_id}. Exception: {type(e).__name__} - {str(e)}")

    @staticmethod
    async def analyze_image(image: UploadFile) -> dict:
        try:
            img_bytes = await image.read()
            # Restoring original intended model for skin diseases
            model_id = os.getenv("HF_IMAGE_MODEL", "Jayanth2002/dinov2-base-finetuned-SkinDisease")
            hf_token = getattr(settings, "HF_TOKEN", os.getenv("HF_TOKEN"))
            
            client = InferenceClient(model=model_id, token=hf_token)
            
            result = client.image_classification(img_bytes)
            
            if isinstance(result, list) and len(result) > 0:
                # `result` is a list of objects that have `.label` and `.score` properties
                # But typically `InferenceClient` returns `list[ImageClassificationOutputElement]`
                top = result[0]
                label = getattr(top, 'label', None)
                score = getattr(top, 'score', None)
                if label is None and isinstance(top, dict):
                    label = top.get("label", "Unknown")
                    score = top.get("score", 0)

                return {
                    "predicted_label": label,
                    "confidence": round(score * 100, 2),
                    "status": "success",
                    "model_id": model_id
                }
            else:
                logger.error(f"HF Inference: No valid predictions returned. Response: {result}")
                raise ValueError("No valid predictions returned from HF model.")

        except Exception as e:
            logger.error(f"Hugging Face unavailable, inference failed: [{type(e).__name__}] {str(e)}")
            return {
                "predicted_label": "Analysis Unavailable",
                "confidence": 0.0,
                "status": "error",
                "error": "Image inference failed or is currently unavailable."
            }
