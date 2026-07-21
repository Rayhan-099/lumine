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
    analysis_result = MLService.analyze_text(description)
    
    image_prediction = None
    if image:
        if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Invalid image format. Please upload a JPG, PNG, or WEBP file.")
        
        # Read file to check size
        img_bytes = await image.read()
        if len(img_bytes) > 10 * 1024 * 1024:
            from fastapi import HTTPException
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")
        
        # We need to reset the file pointer or just pass the bytes directly to MLService
        await image.seek(0)
        logger.info(f"User {current_user.id if current_user else 'Anonymous'} initiated image analysis.")
        image_prediction = await MLService.analyze_image(image)
        logger.info(f"Inference complete: {image_prediction}")
        
    history_context = None
    if current_user:
        past_analyses = db.query(Analysis).filter(Analysis.user_id == current_user.id).order_by(Analysis.timestamp.desc()).limit(5).all()
        history_context = [{"date": a.timestamp.isoformat(), "condition": a.predicted_class or a.text_condition} for a in past_analyses]

    ai_summary = llm_service.generate_report(image_prediction, analysis_result, user_context=history_context)
    
    # Save to history if logged in
    if current_user:
        analysis_record = Analysis(
            user_id=current_user.id,
            predicted_class=image_prediction["predicted_label"] if image_prediction else None,
            confidence=image_prediction["confidence"] if image_prediction else None,
            text_condition=analysis_result["condition"],
            text_seriousness=analysis_result["seriousness"],
            ai_summary=ai_summary,
            recommendations=analysis_result["suggestion"]
        )
        db.add(analysis_record)
        db.commit()
        
    final_response = {
        "text_analysis": analysis_result,
        "image_analysis": image_prediction if image_prediction else None,
        "ai_summary": ai_summary,
        "recommendation": (
            "If symptoms persist or worsen, please consult a certified dermatologist."
            if analysis_result["seriousness"] in ["medium", "high"]
            else "Follow home care suggestions and monitor the condition."
        ),
        "status": "success"
    }

    return final_response
