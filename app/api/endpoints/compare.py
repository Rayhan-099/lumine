from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.analysis import Analysis
from app.models.user import User
from app.services.llm_service import llm_service

router = APIRouter()

@router.get("/")
def compare_analyses(
    id1: int,
    id2: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    a1 = db.query(Analysis).filter(Analysis.id == id1, Analysis.user_id == current_user.id).first()
    a2 = db.query(Analysis).filter(Analysis.id == id2, Analysis.user_id == current_user.id).first()
    
    if not a1 or not a2:
        raise HTTPException(status_code=404, detail="One or both analyses not found")
        
    if a1.confidence <= 0 or a2.confidence <= 0:
        raise HTTPException(status_code=400, detail="One or both selected analyses are invalid or incomplete (0% confidence). Cannot compare.")
        
    # Ensure a1 is the older one
    if a1.timestamp > a2.timestamp:
        a1, a2 = a2, a1
        
    a1_data = {
        "Date": a1.timestamp.isoformat(),
        "Condition": a1.text_condition,
        "AI Prediction": a1.predicted_class,
        "Confidence": a1.confidence
    }
    
    a2_data = {
        "Date": a2.timestamp.isoformat(),
        "Condition": a2.text_condition,
        "AI Prediction": a2.predicted_class,
        "Confidence": a2.confidence
    }
    
    summary = llm_service.generate_comparison(a1_data, a2_data)
        
    return {
        "analysis_1": a1,
        "analysis_2": a2,
        "comparison_summary": summary
    }
