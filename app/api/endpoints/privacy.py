from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.analysis import Analysis
from app.models.user import User

router = APIRouter()

@router.delete("/all")
def delete_all_history(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    try:
        deleted_count = db.query(Analysis).filter(Analysis.user_id == current_user.id).delete()
        db.commit()
        return {"detail": f"Successfully deleted {deleted_count} records."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete history.")

@router.delete("/{analysis_id}")
def delete_history_item(
    analysis_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.user_id == current_user.id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found or unauthorized")
        
    try:
        db.delete(analysis)
        db.commit()
        return {"detail": "Record deleted successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete record.")
