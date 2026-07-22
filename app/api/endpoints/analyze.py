from fastapi import APIRouter, Form, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.services.ml_service import MLService
from app.services.llm_service import llm_service
from app.models.analysis import Analysis
from app.models.user import User
from typing import Optional
from app.core.logging import logger

router = APIRouter()

@router.post("/")
async def analyze_problem(
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
        
        img_bytes = await image.read()
        if len(img_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")
        
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
        past_analyses = db.query(Analysis).filter(Analysis.user_id == current_user.id).order_by(Analysis.timestamp.desc()).limit(5).all()
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
            text_seriousness=analysis_result["seriousness"],
            ai_summary=ai_summary,
            recommendations=analysis_result["suggestion"]
        )
        db.add(analysis_record)
        db.commit()
        
    final_response = {
        "text_analysis": analysis_result,
        "image_analysis": image_prediction,
        "ai_summary": ai_summary,
        "recommendation": (
            "If symptoms persist or worsen, please consult a certified dermatologist."
            if (analysis_result and analysis_result.get("seriousness") in ["medium", "high"])
            else "Follow home care suggestions and monitor the condition."
        ) if analysis_result else None,
        "status": status,
        "user_description": description
    }

    return final_response
