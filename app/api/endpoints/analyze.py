from fastapi import APIRouter, Form, UploadFile, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.api import deps
from app.services.ml_service import MLService
from app.services.llm_service import llm_service
from app.models.analysis import Analysis
from app.models.user import User
from typing import Optional
from app.core.logging import logger
from app.core.rate_limit import limiter
from PIL import Image
import io

# Prevent decompression bombs (max 20 MP)
MAX_IMAGE_WIDTH = 8000
MAX_IMAGE_HEIGHT = 8000
MAX_IMAGE_PIXELS = 20_000_000
Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS

router = APIRouter()

def analyze_rate_limit(key: str):
    # key is either an IP address or a JWT token
    if len(key) > 50:
        return "10/hour"
    return "3/hour"

@router.post("/")
@limiter.limit(analyze_rate_limit)
async def analyze_problem(
    request: Request,
    description: str = Form(...),
    image: UploadFile = None,
    db: Session = Depends(deps.get_db),
    current_user: Optional[User] = Depends(deps.get_optional_current_user)
):
    image_prediction = None
    analysis_result = None
    status = "error"
    
    if image:
        if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
            raise HTTPException(status_code=400, detail="Invalid image format. Please upload a JPG, PNG, or WEBP file.")
        
        img_bytes = b""
        chunk_size = 1024 * 1024 # 1MB
        while True:
            chunk = await image.read(chunk_size)
            if not chunk:
                break
            img_bytes += chunk
            if len(img_bytes) > 10 * 1024 * 1024:
                raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")
        
        try:
            pil_img = Image.open(io.BytesIO(img_bytes))
            width, height = pil_img.size
            if width > MAX_IMAGE_WIDTH or height > MAX_IMAGE_HEIGHT:
                raise HTTPException(status_code=422, detail=f"Image dimensions exceed maximum allowed ({MAX_IMAGE_WIDTH}x{MAX_IMAGE_HEIGHT}).")
            if width * height > MAX_IMAGE_PIXELS:
                raise HTTPException(status_code=422, detail=f"Image pixel count exceeds maximum allowed ({MAX_IMAGE_PIXELS}).")
            pil_img.verify()
        except Image.DecompressionBombWarning:
            raise HTTPException(status_code=413, detail="Image exceeds maximum allowed resolution.")
        except Image.DecompressionBombError:
            raise HTTPException(status_code=413, detail="Image exceeds maximum allowed resolution.")
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid or corrupt image file.")
        
        await image.seek(0)
        logger.info(f"User {current_user.id if current_user else 'Anonymous'} initiated image analysis.")
        image_prediction = await MLService.analyze_image(image)
        logger.info(f"Inference complete: {image_prediction}")
        
        if image_prediction.get("status") == "success":
            status = "success"
            analysis_result = MLService.get_condition_details(image_prediction["predicted_label"])
        else:
            status = "error"
            # If inference fails, do not proceed with text fallbacks
            analysis_result = None

    history_context = None
    if current_user:
        past_analyses = db.query(Analysis).filter(
            Analysis.user_id == current_user.id,
            Analysis.inference_status == "success"
        ).order_by(Analysis.timestamp.desc()).limit(5).all()
        history_context = [{"date": a.timestamp.isoformat(), "condition": a.predicted_class} for a in past_analyses if a.predicted_class]

    ai_summary = None
    if status == "success":
        ai_summary = llm_service.generate_report(image_prediction, analysis_result, user_context=history_context, user_description=description)
        if ai_summary.startswith("AI insights are temporarily unavailable"):
            status = "partial_success"
    
    # Save to history if logged in and ML succeeded
    if current_user and status in ["success", "partial_success"] and analysis_result:
        analysis_record = Analysis(
            user_id=current_user.id,
            predicted_class=image_prediction["predicted_label"],
            confidence=image_prediction["confidence"],
            text_condition=analysis_result["condition"],
            text_seriousness=analysis_result["educational_action_level"],
            ai_summary=ai_summary,
            recommendations=analysis_result["suggestion"],
            inference_status="success",
            model_id=image_prediction.get("model_id"),
            inference_provider="huggingface_serverless"
        )
        db.add(analysis_record)
        db.commit()
        
    final_response = {
        "text_analysis": analysis_result,
        "image_analysis": image_prediction,
        "ai_summary": ai_summary,
        "recommendation": (
            "This visually matches a potentially serious condition. Please consult a certified dermatologist."
            if (analysis_result and analysis_result.get("educational_action_level") == "consult_doctor")
            else "Follow general skincare best practices and monitor."
        ) if analysis_result else None,
        "status": status,
        "user_description": description
    }

    return final_response
