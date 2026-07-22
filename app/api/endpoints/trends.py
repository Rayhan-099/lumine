from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api import deps
from app.models.analysis import Analysis
from app.models.user import User

router = APIRouter()

@router.get("/")
def get_trends(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    analyses = db.query(Analysis).filter(
        Analysis.user_id == current_user.id,
        Analysis.inference_status == "success"
    ).order_by(Analysis.timestamp.asc()).all()
    
    total_analyses = len(analyses)
    if total_analyses == 0:
        return {"total_analyses": 0, "distribution": {}, "timeline": []}
        
    distribution = {}
    timeline = []
    
    for record in analyses:
        # Tally distribution based on AI match or text condition
        label = record.predicted_class if record.predicted_class else record.text_condition
        if not label:
            label = "Unknown"
            
        distribution[label] = distribution.get(label, 0) + 1
        
        timeline.append({
            "date": record.timestamp.isoformat(),
            "condition": label,
            "confidence": record.confidence if record.confidence else 0,
            "seriousness": record.text_seriousness
        })
        
    # Most frequent concern
    most_frequent = max(distribution, key=distribution.get) if distribution else None
    
    return {
        "total_analyses": total_analyses,
        "most_frequent_concern": most_frequent,
        "distribution": distribution,
        "timeline": timeline
    }
