import os
import io
from PIL import Image
from app.core.config import settings
from fastapi import UploadFile
from app.core.logging import logger
from huggingface_hub import InferenceClient

class MLService:
    @staticmethod
    @staticmethod
    def get_condition_details(label: str) -> dict:
        """
        Returns structured educational details ONLY for valid ML predictions.
        Does NOT invent predictions from raw user text.
        Uses exact metadata to prevent hallucinated etiologies.
        """
        metadata_map = {
            "basal cell carcinoma": {
                "brief_description": "A type of skin cancer often appearing as a slightly transparent bump on sun-exposed areas.",
                "general_associations": "Associated with chronic sun exposure or UV radiation.",
                "educational_action_level": "consult_doctor"
            },
            "squamous cell carcinoma": {
                "brief_description": "A common form of skin cancer that develops in the squamous cells of the epidermis.",
                "general_associations": "Associated with prolonged UV exposure.",
                "educational_action_level": "consult_doctor"
            },
            "melanoma": {
                "brief_description": "A serious type of skin cancer that develops in the cells that produce melanin.",
                "general_associations": "Associated with UV exposure and genetic factors.",
                "educational_action_level": "consult_doctor"
            },
            "actinic keratosis": {
                "brief_description": "A rough, scaly patch on the skin that develops from years of exposure to the sun.",
                "general_associations": "Associated with chronic sun damage. Considered precancerous.",
                "educational_action_level": "consult_doctor"
            },
            "psoriasis": {
                "brief_description": "A skin disease that causes a rash with itchy, scaly patches.",
                "general_associations": "Associated with an immune system response triggering rapid skin cell turnover.",
                "educational_action_level": "manage_flareups"
            },
            "herpes simplex": {
                "brief_description": "A viral infection causing contagious sores.",
                "general_associations": "Associated with the Herpes Simplex Virus (HSV).",
                "educational_action_level": "manage_flareups"
            },
            "impetigo": {
                "brief_description": "A highly contagious skin infection that mainly affects infants and children.",
                "general_associations": "Associated with bacterial infection (Staphylococcus or Streptococcus).",
                "educational_action_level": "consult_doctor"
            },
            "larva migrans": {
                "brief_description": "A creeping eruption caused by hookworm larvae migrating under the skin.",
                "general_associations": "Associated with parasitic infection often contracted from contaminated soil or sand.",
                "educational_action_level": "consult_doctor"
            },
            "tinea corporis": {
                "brief_description": "A superficial fungal infection (ringworm) of the arms and legs.",
                "general_associations": "Associated with dermatophyte fungal infection.",
                "educational_action_level": "treat_infection"
            },
            "tinea nigra": {
                "brief_description": "A superficial fungal infection that causes dark brown to black painless patches.",
                "general_associations": "Associated with the fungus Hortaea werneckii, often from soil.",
                "educational_action_level": "treat_infection"
            },
            "leprosy lepromatous": {
                "brief_description": "A chronic, progressive bacterial infection causing severe skin sores.",
                "general_associations": "Associated with Mycobacterium leprae.",
                "educational_action_level": "consult_doctor"
            },
            "leprosy tuberculoid": {
                "brief_description": "A form of leprosy characterized by pale skin macules and nerve damage.",
                "general_associations": "Associated with Mycobacterium leprae.",
                "educational_action_level": "consult_doctor"
            },
            "leprosy borderline": {
                "brief_description": "An intermediate form of leprosy exhibiting features of both types.",
                "general_associations": "Associated with Mycobacterium leprae.",
                "educational_action_level": "consult_doctor"
            },
            "molluscum contagiosum": {
                "brief_description": "A viral infection of the skin that results in round, firm, painless bumps.",
                "general_associations": "Associated with a poxvirus.",
                "educational_action_level": "monitor_closely"
            },
            "pediculosis capitis": {
                "brief_description": "An infestation of the scalp by the head louse.",
                "general_associations": "Associated with parasitic lice.",
                "educational_action_level": "treat_infection"
            },
            "tungiasis": {
                "brief_description": "An inflammatory skin disease caused by infection with the female sand flea.",
                "general_associations": "Associated with the Tunga penetrans flea.",
                "educational_action_level": "consult_doctor"
            },
            "dermatofibroma": {
                "brief_description": "A common benign skin growth that often appears on the lower legs.",
                "general_associations": "Often unknown cause, possibly a reaction to minor trauma or bug bites.",
                "educational_action_level": "monitor_closely"
            },
            "nevus": {
                "brief_description": "A common benign pigmented spot on the skin, typically a mole.",
                "general_associations": "Associated with clusters of melanocytes.",
                "educational_action_level": "monitor_closely"
            },
            "pigmented benign keratosis": {
                "brief_description": "A non-cancerous skin growth that can appear dark or pigmented.",
                "general_associations": "Often age-related or sun-related, but benign.",
                "educational_action_level": "monitor_closely"
            },
            "seborrheic keratosis": {
                "brief_description": "One of the most common noncancerous skin growths in older adults.",
                "general_associations": "Associated with aging and genetic predisposition.",
                "educational_action_level": "monitor_closely"
            },
            "vascular lesion": {
                "brief_description": "A relatively common abnormality of the skin and underlying tissues.",
                "general_associations": "Associated with abnormal blood vessels.",
                "educational_action_level": "monitor_closely"
            },
            "darier_s disease": {
                "brief_description": "A rare genetic skin disorder characterized by wart-like blemishes on the body.",
                "general_associations": "Associated with a genetic mutation affecting skin cell adhesion.",
                "educational_action_level": "consult_doctor"
            },
            "epidermolysis bullosa pruriginosa": {
                "brief_description": "A rare genetic disorder causing itchy, blistering skin.",
                "general_associations": "Associated with genetic mutations affecting structural proteins in the skin.",
                "educational_action_level": "consult_doctor"
            },
            "hailey-hailey disease": {
                "brief_description": "A rare genetic condition characterized by blisters and erosions.",
                "general_associations": "Associated with a genetic mutation.",
                "educational_action_level": "consult_doctor"
            },
            "lichen planus": {
                "brief_description": "An inflammatory condition that can affect the skin.",
                "general_associations": "Associated with an abnormal immune response.",
                "educational_action_level": "manage_flareups"
            },
            "lupus erythematosus chronicus discoides": {
                "brief_description": "A chronic skin condition of sores with inflammation and scarring.",
                "general_associations": "Associated with autoimmune disease.",
                "educational_action_level": "consult_doctor"
            },
            "mycosis fungoides": {
                "brief_description": "A rare type of blood cancer (cutaneous T-cell lymphoma) that affects the skin.",
                "general_associations": "Associated with abnormal T-cells.",
                "educational_action_level": "consult_doctor"
            },
            "neurofibromatosis": {
                "brief_description": "A genetic disorder that causes tumors to form on nerve tissue.",
                "general_associations": "Associated with a genetic mutation.",
                "educational_action_level": "consult_doctor"
            },
            "papilomatosis confluentes and reticulate": {
                "brief_description": "A rare skin condition characterized by a scaly, pigmented rash.",
                "general_associations": "Cause is not fully understood, possibly related to an abnormal response to yeast.",
                "educational_action_level": "consult_doctor"
            },
            "pityriasis rosea": {
                "brief_description": "A skin rash that sometimes begins as a large spot on the chest, belly, or back.",
                "general_associations": "Possibly associated with a viral infection.",
                "educational_action_level": "monitor_closely"
            },
            "porokeratosis actinic": {
                "brief_description": "A skin condition characterized by multiple small, sun-damaged patches.",
                "general_associations": "Associated with sun exposure and genetics.",
                "educational_action_level": "monitor_closely"
            }
        }
        
        label_lower = label.lower()
        if label_lower in metadata_map:
            metadata = metadata_map[label_lower]
            return {
                "condition": label, # display name matches the label from the model directly
                "causes": metadata["general_associations"],
                "suggestion": metadata["brief_description"],
                "educational_action_level": metadata["educational_action_level"]
            }
        else:
            logger.warning(f"ML Warning: Unknown model label received '{label}' - no educational metadata available.")
            return {
                "condition": label,
                "causes": "Information unavailable.",
                "suggestion": "Educational information is unavailable for this classification.",
                "educational_action_level": "unknown"
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
            
            try:
                # Validate uploaded image, normalize to RGB (removes alpha/transparency), and re-encode to valid JPEG bytes
                pil_img = Image.open(io.BytesIO(img_bytes))
                if pil_img.mode != "RGB":
                    pil_img = pil_img.convert("RGB")
                    
                out_bytes = io.BytesIO()
                pil_img.save(out_bytes, format="JPEG")
                jpeg_bytes = out_bytes.getvalue()
            except Exception as e:
                logger.error(f"Image validation failed: {e}")
                return {
                    "predicted_label": "Analysis Unavailable",
                    "confidence": 0.0,
                    "status": "error",
                    "error": "Invalid image format uploaded."
                }
            
            # Restoring original intended model for skin diseases
            model_id = os.getenv("HF_IMAGE_MODEL", "Jayanth2002/dinov2-base-finetuned-SkinDisease")
            hf_token = getattr(settings, "HF_TOKEN", os.getenv("HF_TOKEN"))
            
            # Fix: Explicitly send Content-Type header so Hugging Face accepts the raw bytes payload
            client = InferenceClient(
                model=model_id, 
                token=hf_token, 
                headers={"Content-Type": "image/jpeg"}
            )
            
            result = client.image_classification(jpeg_bytes)
            
            if isinstance(result, list) and len(result) > 0:
                parsed_predictions = []
                for item in result:
                    l = getattr(item, 'label', None)
                    s = getattr(item, 'score', None)
                    if l is None and isinstance(item, dict):
                        l = item.get("label", "Unknown")
                        s = item.get("score", 0)
                    parsed_predictions.append({"label": l, "score": round(s * 100, 2)})
                
                parsed_predictions.sort(key=lambda x: x["score"], reverse=True)
                top = parsed_predictions[0]
                
                is_ambiguous = False
                if len(parsed_predictions) > 1:
                    margin = top["score"] - parsed_predictions[1]["score"]
                    if margin < 15.0:
                        is_ambiguous = True

                return {
                    "predicted_label": top["label"],
                    "confidence": top["score"],
                    "status": "success",
                    "model_id": model_id,
                    "top_predictions": parsed_predictions[:3],
                    "is_ambiguous": is_ambiguous
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
