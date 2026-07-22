from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.api import deps
from app.models.analysis import Analysis
from app.models.user import User
from app.services.llm_service import llm_service

router = APIRouter()

@router.post("/ask")
def ask_assistant(
    question: str = Body(..., embed=True),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    past_analyses = db.query(Analysis).filter(
        Analysis.user_id == current_user.id,
        Analysis.confidence > 0
    ).order_by(Analysis.timestamp.desc()).limit(10).all()
    
    history_context = []
    for a in past_analyses:
        history_context.append({
            "Date": a.timestamp.isoformat(),
            "Condition": a.text_condition,
            "Prediction": a.predicted_class,
            "Confidence": a.confidence
        })
        
    prompt = f"""
    You are Lumine AI, an intelligent, empathetic digital skin health assistant.
    The user is asking you a question about their skin history or general skin health.
    
    User's Recent History: {history_context}
    
    User's Question: "{question}"
    
    Provide a helpful, conversational answer. Use the historical context if relevant (e.g. "I see you've had Acne in your last 3 scans").
    CRITICAL RULE: You are an informational assistant, NOT a doctor. You must never provide a definitive medical diagnosis. If the question asks for a diagnosis or the condition sounds serious, tell them to consult a certified dermatologist.
    """
    
    try:
        answer = llm_service.generate_assistant_response(prompt)
    except Exception as e:
        answer = "I'm sorry, I couldn't process your request right now."
        
    return {"answer": answer}
