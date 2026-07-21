from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.models.analysis import Analysis
from app.models.user import User

router = APIRouter()

@router.get("/")
def get_history(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    analyses = db.query(Analysis).filter(Analysis.user_id == current_user.id).order_by(Analysis.timestamp.desc()).all()
    return analyses
